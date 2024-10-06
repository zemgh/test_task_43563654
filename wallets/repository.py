import uuid

from fastapi import HTTPException
from sqlalchemy import select, insert, update
from starlette import status

from models import Wallet


class WalletRepository:

    def __init__(self, db, cache=None):
        self._db = db
        self._cache_client = cache


    async def get_wallet(self, wallet_uuid: str) -> Wallet:
        cached_wallet = await self._get_cache(wallet_uuid)
        if cached_wallet:
            return cached_wallet

        query = select(Wallet).where(Wallet.uuid == wallet_uuid)
        wallet = await self._db.scalar(query)

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet with uuid '{wallet_uuid}' not found"
            )

        await self._set_cache(wallet_uuid, wallet.balance)
        return wallet


    async def create_wallet(self) -> Wallet:
        uuid = self._create_uuid()

        query = insert(Wallet).values(uuid=uuid, balance=0).returning(Wallet)
        result = await self._db.execute(query)
        await self._db.commit()

        return self._row_to_model(result)


    async def update_wallet(self, wallet_uuid: str, amount: int) -> Wallet:
        async with self._db.begin():
            wallet = await self.get_wallet(wallet_uuid)
            new_balance = wallet.balance + amount

            print(new_balance)
            if new_balance < 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"insufficient funds in wallet with uuid '{wallet_uuid}'"
                )

            query = update(Wallet).where(Wallet.uuid == wallet.uuid).values(balance=new_balance).returning(Wallet)
            result = await self._db.execute(query)

            wallet = self._row_to_model(result)
            await self._set_cache(wallet_uuid, wallet.balance)

            return wallet


    async def _get_cache(self, key) -> Wallet:
        if self._cache_client:
            balance = await self._cache_client.get(key)
            if balance:
                return Wallet(uuid=key, balance=int(balance))


    async def _set_cache(self, uuid, balance):
        if self._cache_client:
            await self._cache_client.set(uuid, balance)


    @staticmethod
    def _create_uuid() -> uuid:
        return str(uuid.uuid4())


    @staticmethod
    def _row_to_model(result) -> Wallet:
        row = result.fetchone()
        model = row[0]
        return model




