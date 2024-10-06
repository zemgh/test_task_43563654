import asyncio
import os

import redis.asyncio as redis

from dotenv import load_dotenv


class RedisClient:
    def __init__(self, host, port=6379):
        self._host = host
        self._port = port
        self._connection = None

    async def connect(self):
        load_dotenv()
        timeout = float(os.getenv('REDIS_CONNECT_TIMEOUT', 1))

        try:
            self._connection = await redis.Redis(host=self._host, port=self._port, socket_connect_timeout=timeout)
        except Exception as e:
            print('Redis error: ', e)

    async def disconnect(self):
        try:
            await self._connection.close()
        except Exception as e:
            print('Redis error: ', e)

    async def get_status(self):
        try:
            return await self._connection.ping()
        except Exception as e:
            print('Redis error: ', e)

    async def set(self, key, value):
        await self._connection.set(key, value)

    async def get(self, key):
        return await self._connection.get(key)


load_dotenv()

redis_client: RedisClient = None
MONITORING = os.getenv('REDIS_MONITORING', True)
FREQUENCY = int(os.getenv('REDIS_MONITORING_FREQUENCY', 15))


def get_redis():
    global redis_client
    return redis_client


async def redis_cli_connect():
    global redis_client
    load_dotenv()
    host = os.environ.get('REDIS_HOST', 'localhost')
    port = int(os.environ.get('REDIS_PORT', 6379))

    client = RedisClient(host, port)
    await client.connect()

    if await client.get_status():
        redis_client = client
        print('Connected to redis')


async def redis_monitor_status():
    global redis_client
    global MONITORING
    global FREQUENCY

    if MONITORING:
        while True:
            await asyncio.sleep(FREQUENCY)

            if not redis_client:
                await redis_cli_connect()
            else:
                if not await redis_client.get_status():
                    await redis_cli_disconnect()
                    await redis_cli_connect()


async def redis_cli_disconnect():
    global redis_client
    await redis_client.disconnect()
    redis_client = None

