import os

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from fastapi import HTTPException
from starlette import status

load_dotenv()

DEBUG = os.getenv("DEBUG")

SQLALCHEMY_DATABASE_URL = os.getenv('DB_URL')

# SQLALCHEMY_DATABASE_URL = 'postgresql+asyncpg://wallets_user:qwerty@localhost:5432/wallets_db'

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_db() -> AsyncSession:
    try:
        async with async_session() as session:
            yield session
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={'message': 'Database Error'}
        )