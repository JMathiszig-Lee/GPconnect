import os
import sys

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")


def redis_connect() -> redis.Redis:
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=6379,
        )
        ping = client.ping()
        if ping is True:
            return client
    except:
        print("Redis Error")
        sys.exit(1)


redis_client = redis_connect()
