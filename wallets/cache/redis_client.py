import os

from dotenv import load_dotenv

import redis.asyncio as redis


class RedisClient:
    def __init__(self, host, port, func):
        self._host = host
        self._port = port
        self._connection = None
        self._redis_cli_disconnect = func


    async def connect(self):
        load_dotenv()
        timeout = float(os.getenv('REDIS_CONNECT_TIMEOUT', 1))


        try:
            self._connection = await redis.Redis(host=self._host, port=self._port, socket_connect_timeout=timeout)
        except Exception as e:
            # log
            pass


    async def disconnect(self):
        try:
            await self._connection.close()
        except Exception as e:
            # log
            pass


    async def get_status(self):
        try:
            return await self._connection.ping()
        except Exception as e:
            pass
            # log


    async def set(self, key, value):
        try:
            await self._connection.set(key, value)
        except Exception as e:
            # log
            await self._redis_cli_disconnect()


    async def get(self, key):
        try:
            return await self._connection.get(key)
        except Exception as e:
            # log
            await self._redis_cli_disconnect()
