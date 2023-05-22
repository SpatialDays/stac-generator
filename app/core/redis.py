import redis
from loguru import logger
import json
from app.stac.services.stac_item_creator import STACItemCreator


def create_redis_connection(host: str, port: int, db: int):
    return redis.Redis(host=host, port=port, db=db)


def redis_listener(redis_conn, app):
    while True:
        item = redis_conn.blpop(app.state.redis_queue_key, timeout=1)
        if item:
            logger.info(f"Received item from Redis: {item}")
            _, job_dict = item
            item_dict = json.loads(job_dict)
            stac = STACItemCreator(item_dict).create_item()
            # rpush the stac item to redis
            redis_conn.rpush("stac_generator_stac", json.dumps(stac))
