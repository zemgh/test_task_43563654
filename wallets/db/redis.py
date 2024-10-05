import os

import redis.asyncio as redis
from dotenv import load_dotenv


class RedisClient:
    def __init__(self, host, port=6379):
        self._host = host
        self._port = port
        self._redis = None

    async def connect(self):
        self._redis = await redis.Redis(host=self._host, port=self._port, socket_connect_timeout=0.5)
        await self._redis.ping()

    async def disconnect(self):
        try:
            await self._redis.close()
        except Exception as e:
            print(e)

    async def set(self, key, value):
        await self._redis.set(key, value)

    async def get(self, key, object_model):
        """
        :return: SQLModel(object_model)
        """
        value = await self._redis.get(key)
        if value:
            result = object_model(uuid=key, balance=int(value))
            return result


redis_cli: RedisClient = None


async def start_redis():
    global redis_cli
    load_dotenv()


    redis_url = os.environ.get('REDIS_HOST')
    # redis_url = 'localhost'

    redis_cli = RedisClient(redis_url, 6379)
    try:
        await redis_cli.connect()
        print('Connected to redis')
    except Exception as e:
        print('Redis error:', e)
        redis_cli = None


async def get_redis():
    global redis_cli
    return redis_cli
