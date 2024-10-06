from typing import Annotated
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.postgres import get_db
from db.redis import RedisClient, get_redis
from repository import WalletRepository
from schemas import WalletOperationSchema
from services import WalletService

router = APIRouter(prefix='/api/v1/wallets')


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_wallet(db: Annotated[AsyncSession, Depends(get_db)]):

    repository = WalletRepository(db)
    wallet = await repository.create_wallet()
    return wallet


@router.get('/{wallet_uuid}')
async def get_wallet(wallet_uuid: str,
                     db: Annotated[AsyncSession, Depends(get_db)],
                     cache: Annotated[RedisClient, Depends(get_redis)]):

    repository = WalletRepository(db, cache)
    wallet = await repository.get_wallet(wallet_uuid)
    return wallet


@router.post('/{wallet_uuid}/operation', status_code=status.HTTP_200_OK)
async def handle_wallet_operation(wallet_uuid: str,
                                  data: WalletOperationSchema,
                                  db: Annotated[AsyncSession, Depends(get_db)],
                                  cache: Annotated[RedisClient, Depends(get_redis)]):

    repository = WalletRepository(db, cache)
    service = WalletService(repository)
    wallet = await service.process_operation(wallet_uuid, data)

    return {
        'status': 'success',
        'operationType': data.operationType,
        'amount': data.amount,
        'wallet': wallet
    }


