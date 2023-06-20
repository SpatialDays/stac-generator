import redis
from loguru import logger
import json
from os import getenv
from dotenv import load_dotenv

from app.stac.services.stac_item_creator import STACItemCreator
from app.stac.services.publisher.publisher_utility import publish_to_stac_fastapi

load_dotenv(".env")

REDIS_HOST = getenv("REDIS_HOST")
REDIS_PORT = int(getenv("REDIS_PORT"))
REDIS_DB = int(getenv("REDIS_DB", 0))
REDIS_OUTPUT_LIST_NAME = getenv("REDIS_OUTPUT_LIST_NAME", "stac_generator_output")


def create_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def redis_listener(redis_conn, app):
    if not redis_conn:
        logger.warning("No Redis connection, redis_listener will not run.")
        return

    while True:
        try:
            item = redis_conn.blpop(app.state.redis_queue_key, timeout=1)
            if item:
                logger.info(f"Received item from Redis: {item}")
                _, job_dict = item
                item_dict = json.loads(job_dict)
                stac = STACItemCreator(item_dict).create_item()

                collection = item.collection or item.parser or "default"

                if getenv("REDIS_PUBLISH_TO_STAC_API").lower() == "true":
                    redis_conn.rpush(
                        REDIS_OUTPUT_LIST_NAME,
                        json.dumps({"collection": collection, "stac": stac}),
                    )

                if getenv("HTTP_PUBLISH_TO_STAC_API").lower() == "true":
                    try:
                        return publish_to_stac_fastapi(stac, collection)
                    except Exception as e:
                        logger.error(f"Error publishing to STAC API: {e}")
                        break

        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            break
        except Exception as e:
            logger.error(f"Error processing item: {e}")
