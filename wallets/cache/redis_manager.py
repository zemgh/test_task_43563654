import asyncio
import os

from dotenv import load_dotenv

from cache.redis_client import RedisClient

REDIS: RedisClient = None


def get_redis():
    global REDIS
    return REDIS


async def redis_cli_connect():
    global REDIS
    load_dotenv()
    host = os.environ.get('REDIS_HOST')
    port = int(os.environ.get('REDIS_PORT', 6379))

    # config = get_config('redis')

    client = RedisClient(host, port, redis_cli_disconnect)
    await client.connect()

    if await client.get_status():
        REDIS = client
        print('Redis: connected')


async def redis_cli_disconnect():
    global REDIS
    if REDIS:
        await REDIS.disconnect()
    REDIS = None
    print('Redis: disconnected')


async def redis_monitor_status():
    global REDIS
    load_dotenv()

    monitoring = os.getenv('REDIS_MONITORING', True)
    if monitoring:
        while True:

            frequency = int(os.getenv('REDIS_MONITORING_FREQUENCY', 15))
            await asyncio.sleep(frequency)

            if not REDIS:
                await redis_cli_connect()

            else:
                if not await REDIS.get_status():
                    await redis_cli_disconnect()
                    await redis_cli_connect()



