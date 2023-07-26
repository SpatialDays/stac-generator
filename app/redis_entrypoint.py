import redis
import os

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Starting Redis listener")
logging.info("Starting Redis listener")

from app.core.redis import redis_listener

_REDIS_HOST = os.getenv("REDIS_HOST")
_REDIS_PORT = int(os.getenv("REDIS_PORT"))

if __name__ == "__main__":
    redis_connection = redis.Redis(
        host=_REDIS_HOST, port=_REDIS_PORT)

    if redis_connection.ping():
        logging.info("Connected to Redis")
    else:
        logging.error("Could not connect to Redis")
        exit(1)
        
    redis_listener(redis_connection)