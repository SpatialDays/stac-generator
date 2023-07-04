import redis
import os
from app.core.redis import redis_listener
import logging
logging.basicConfig(level=logging.INFO)

_REDIS_HOST = os.getenv("REDIS_HOST")
_REDIS_PORT = int(os.getenv("REDIS_PORT"))
_REDIS_DB = int(os.getenv("REDIS_DB", 0))

if __name__ == "__main__":
    redis_connection = redis.Redis(
        host=_REDIS_HOST, port=_REDIS_PORT, db=_REDIS_DB)

    if redis_connection.ping():
        logging.info("Connected to Redis")
    else:
        logging.error("Could not connect to Redis")
        exit(1)
        
    redis_listener(redis_connection)