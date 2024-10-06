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
        load_dotenv()
        timeout = int(os.getenv('CONNECT_TIMEOUT', 1))
        self._redis = await redis.Redis(host=self._host, port=self._port, socket_connect_timeout=timeout)
        await self._redis.ping()

    async def disconnect(self):
        try:
            await self._redis.close()
        except Exception as e:
            print(e)

    async def set(self, key, value):
        print('set chache')
        await self._redis.set(key, value)

    async def get(self, key):
        print('get chache')
        return await self._redis.get(key)


load_dotenv()

REDIS: RedisClient = None
RECONNECT = os.getenv('RECONNECT', True)
RECONNECT_DELAY = int(os.getenv('RECONNECT_DELAY', 60))


async def get_redis():
    global REDIS
    return REDIS


async def redis_connect():
    global REDIS
    load_dotenv()
    host = os.environ.get('REDIS_HOST', 'localhost')
    port = int(os.environ.get('REDIS_PORT', 6379))

    redis = RedisClient(host, port)

    try:
        await redis.connect()
        REDIS = redis
        print('Connected to redis')

    except Exception as e:
        print('Redis error:', e)


async def redis_monitor():
    global RECONNECT
    global RECONNECT_DELAY

    if RECONNECT:
        while True:

            await asyncio.sleep(RECONNECT_DELAY)
            if not REDIS:
                await redis_connect()


async def redis_close():
    global REDIS
    REDIS = None

    try:
        await REDIS.disconnect()

    except AttributeError:
        print('Redis error: no connection')

    except Exception as e:
        print('Redis error:', e)

    finally:
        print('Redis closed')
