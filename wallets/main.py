from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from db.redis import start_redis, stop_redis
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_redis()
    yield
    await stop_redis()


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={'message': 'Server Error'},
    )

