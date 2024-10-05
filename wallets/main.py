from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from db.redis import close_redis, connect_redis
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_redis()
    yield
    await close_redis()


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={'message': 'Server Error'},
    )

