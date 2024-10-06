import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from cache.redis_manager import redis_monitor_status, redis_cli_connect, redis_cli_disconnect
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_cli_connect()
    asyncio.create_task(redis_monitor_status())
    yield
    await redis_cli_disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            'message': 'Server Error',
            'request_url': str(request.url),
            'error': str(exc)
            }
    )
