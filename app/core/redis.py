import redis
from loguru import logger
import json
from os import getenv
from dotenv import load_dotenv

from app.stac.services.stac_item_creator import STACItemCreator
from app.stac.services.publisher.publisher_utility import publish_to_stac_fastapi

load_dotenv()

REDIS_INPUT_LIST_NAME = getenv("REDIS_INPUT_LIST_NAME", "stac_generator_input")
REDIS_OUTPUT_LIST_NAME = getenv("REDIS_OUTPUT_LIST_NAME", "stac_generator_output")

def redis_listener(redis_conn):
    if not redis_conn:
        logger.warning("No Redis connection, redis_listener will not run.")
        return
    logger.info(f"Running redis_listener on {REDIS_INPUT_LIST_NAME}")
    logger.info(f"Publishing to {REDIS_OUTPUT_LIST_NAME}")
    while True:
        try:
            item = redis_conn.blpop(REDIS_INPUT_LIST_NAME, timeout=1)
            if item:
                logger.info(f"Received item from Redis: {item}")
                _, job_dict = item
                item_dict = json.loads(job_dict)
                stac = STACItemCreator(item_dict).create_item()

                collection = (
                        item_dict.get("collection") or item_dict.get("parser") or "default"
                )

                if getenv("REDIS_PUBLISH_TO_STAC_API") is not None and getenv("REDIS_PUBLISH_TO_STAC_API").lower() == "true":
                    redis_conn.rpush(
                        REDIS_OUTPUT_LIST_NAME,
                        json.dumps({"collection": collection, "stac": stac}),
                    )

                if getenv("HTTP_PUBLISH_TO_STAC_API") is not None and getenv("HTTP_PUBLISH_TO_STAC_API").lower() == "true":
                    try:
                        publish_to_stac_fastapi(stac, collection)
                    except Exception as e:
                        logger.error(f"Error publishing to STAC API: {e}")
                        break

        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            break
        # not catching this makes it eaiser to debug, as this exception is raised any of the functions and in the try
        # block fail subfunctions in the try block fail except Exception as e: logger.error(f"Error processing item:

        # except Exception as e:
        #     logger.error(f"Error processing item: {e}")
