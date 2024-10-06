import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from db.redis import redis_connect, redis_close, redis_monitor
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_connect()
    asyncio.create_task(redis_monitor())
    yield
    await redis_close()


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            'message': 'Server Error'
            }
    )

