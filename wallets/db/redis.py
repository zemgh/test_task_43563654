import asyncio
import os

import redis.asyncio as redis
from dotenv import load_dotenv


class RedisClient:
    def __init__(self, host, port=6379):
        self._host = host
        self._port = port
        self._redis = None

    async def connect(self):
        self._redis = await redis.Redis(host=self._host, port=self._port, socket_connect_timeout=3)
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


async def connect_redis():
    global redis_cli
    load_dotenv()


    redis_url = os.environ.get('REDIS_HOST')
    # redis_url = 'localhost'

    redis = RedisClient(redis_url, 6379)
    try:
        await redis.connect()
        redis_cli = redis
        print('Connected to redis')
    except Exception as e:
        print('Redis error:', e)


async def close_redis(reconnect=True):
    global redis_cli
    redis_cli = None

    try:
        await redis_cli.disconnect()

    except AttributeError:
        print('Redis error: no connection')

    except Exception as e:
        print(type(e))
        print('Redis error:', e.__dict__)

    finally:
        print('Redis closed')
        if reconnect:
            await reconnect_redis()


async def get_redis():
    global redis_cli
    return redis_cli


async def reconnect_redis(delay=10, attempts=None):
    global redis_cli
    count = 0
    while not attempts or count < attempts:
        print('Trying to reconnect redis ...')
        await asyncio.sleep(delay)
        await connect_redis()

        if redis_cli:
            break
        count += 1


