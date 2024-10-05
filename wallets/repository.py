import uuid

from fastapi import HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.exc import IntegrityError
from starlette import status

from models import Wallet


class WalletRepository:

    def __init__(self, db, cache=None):
        self.db = db
        self.cache = cache

    async def get_wallet(self, wallet_uuid: str) -> Wallet:
        cached_wallet = await self._get_cache(wallet_uuid, Wallet)
        if cached_wallet:
            return cached_wallet

        query = select(Wallet).where(Wallet.uuid == wallet_uuid)
        wallet = await self.db.scalar(query)

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet with uuid '{wallet_uuid}' not found"
            )

        await self._cache(wallet_uuid, wallet.balance)
        return wallet

    async def create_wallet(self) -> Wallet:
        for attempt in range(11):
            uuid = self._create_uuid()
            query = insert(Wallet).values(uuid=uuid, balance=0).returning(Wallet)

            try:
                result = await self.db.execute(query)
                await self.db.commit()
                return self._result_to_model(result)

            except IntegrityError:
                await self.db.rollback()
                if attempt == 10:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create wallet after multiple attempts"
                    )

    async def update_balance(self, wallet_uuid: str, amount: int) -> Wallet:
        async with self.db.begin():
            wallet = await self.get_wallet(wallet_uuid)
            new_balance = wallet.balance + amount

            if new_balance >= 0:
                query = update(Wallet).where(Wallet.uuid == wallet.uuid).values(balance=new_balance).returning(Wallet)
                result = await self.db.execute(query)

                wallet = self._result_to_model(result)
                await self._cache(wallet_uuid, wallet.balance)

                return wallet

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"insufficient funds in wallet with uuid '{wallet_uuid}'"
            )

    async def _get_cache(self, key, object_type) -> Wallet:
        if self.cache:
            return await self.cache.get(key, object_type)

    async def _cache(self, uuid, balance):
        if self.cache:
            await self.cache.set(uuid, balance)


    @staticmethod
    def _create_uuid() -> uuid:
        return str(uuid.uuid4())

    @staticmethod
    def _result_to_model(result) -> Wallet:
        row = result.fetchone()
        model = row[0]

        if model:
            return model

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Something went wrong'
        )



