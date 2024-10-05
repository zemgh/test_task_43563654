from fastapi import HTTPException
from starlette import status

from models import Wallet
from repository import WalletRepository
from schemas import WalletOperationSchema


class WalletService:
    __ALLOWED_OPERATIONS = ['deposit', 'withdraw']

    def __init__(self, repository: WalletRepository):
        self.repository = repository

    async def process_operation(self, wallet_uuid: str, data: WalletOperationSchema) -> Wallet:
        operation = data.operationType.lower()

        if operation not in self.__ALLOWED_OPERATIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Operation type '{operation}' not allowed"
            )

        method = getattr(self, f'_{operation}')
        return await method(wallet_uuid, data.amount)

    async def _deposit(self, wallet_uuid: str, amount: int) -> Wallet:
        return await self._update_balance(wallet_uuid, amount)

    async def _withdraw(self, wallet_uuid: str, amount: int) -> Wallet:
        if amount > 0:
            amount = -amount
        return await self._update_balance(wallet_uuid, amount)

    async def _update_balance(self, wallet_uuid: str, amount: int) -> Wallet:
        return await self.repository.update_balance(wallet_uuid, amount)







