import sys

import redis


def redis_connect() -> redis.Redis:
    try:
        client = redis.Redis(
            host="localhost",
            port=6379,
        )
        ping = client.ping()
        if ping is True:
            return client
    except:
        print("Redis Error")
        sys.exit(1)
