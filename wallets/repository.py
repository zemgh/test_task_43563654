import asyncio
import json
import uuid

from fastapi import HTTPException
from sqlalchemy import select, insert, update
from starlette import status

from db.redis import redis_close
from models import Wallet


class WalletRepository:

    def __init__(self, db, cache=None):
        self._db = db
        self._cache = cache

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

        return self._result_to_model(result)


    async def update_balance(self, wallet_uuid: str, amount: int) -> Wallet:
        async with self._db.begin():
            wallet = await self.get_wallet(wallet_uuid)
            new_balance = wallet.balance + amount

            if new_balance >= 0:
                query = update(Wallet).where(Wallet.uuid == wallet.uuid).values(balance=new_balance).returning(Wallet)
                result = await self._db.execute(query)

                wallet = self._result_to_model(result)
                await self._set_cache(wallet_uuid, wallet.balance)

                return wallet

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"insufficient funds in wallet with uuid '{wallet_uuid}'"
            )

    async def _get_cache(self, key) -> Wallet:
        try:
            if self._cache:
                balance = await self._cache.get(key)
                if balance:
                    return Wallet(uuid=key, balance=int(balance))

        except Exception as e:
            self._cache = None
            self._close()
            print('Cache Error:', e)

    async def _set_cache(self, uuid, balance):
        try:
            if self._cache:
                await self._cache.set(uuid, balance)

        except Exception as e:
            self._cache = None
            self._close()
            print('Cache Error:', e)

    @staticmethod
    def _close():
        asyncio.create_task(redis_close())

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



