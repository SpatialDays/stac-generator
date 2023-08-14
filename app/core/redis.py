import os

import redis
import logging

logger = logging.getLogger(__name__)

import json
from os import getenv
from dotenv import load_dotenv

from app.stac.services.stac_item_creator import STACItemCreator
from app.stac.services.publisher.publisher_utility import publish_to_stac_fastapi
from app.stac.services.blob_mounting.blob_mapping_utility import blob_mapping_utility

load_dotenv()

REDIS_INPUT_LIST_NAME = getenv("REDIS_INPUT_LIST_NAME", "stac_generator_input")
REDIS_OUTPUT_LIST_NAME = getenv("REDIS_OUTPUT_LIST_NAME", "stac_generator_output")
DOWNLOAD_ASSETS_FROM_URLS = getenv("DOWNLOAD_ASSETS_FROM_URLS", "false").lower() == "true"
_CLEANUP_DOWNLOADED_FILES = getenv("CLEANUP_DOWNLOADED_FILES", "true").lower() == "true"


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
                logger.info("Timing start")
                logger.info("Received item from Redis")
                # logger.debug(f"Received item from Redis: {item}")
                _, job_dict = item
                item_dict = json.loads(job_dict)
                files_for_download = item_dict.get("files_converted_to_cog", [])
                files_for_download.append(item_dict.get("metadata_url"))
                files_for_download = list(set(files_for_download))
                if DOWNLOAD_ASSETS_FROM_URLS:
                    for file in files_for_download:
                        try:
                            blob_mapping_utility.download_blob(file)
                        except Exception as e:
                            logger.debug(
                                f"File {file} could not be downloaded. Probably not part of a storage account.")
                stac = STACItemCreator(item_dict).create_item()
                logger.info(f"Created STAC item")

                collection = (
                        item_dict.get("collection") or item_dict.get("parser") or "default"
                )

                if getenv("REDIS_PUBLISH_TO_STAC_API") is not None and getenv(
                        "REDIS_PUBLISH_TO_STAC_API").lower() == "true":
                    logger.info("Publishing to Redis")
                    redis_conn.rpush(
                        REDIS_OUTPUT_LIST_NAME,
                        json.dumps({"collection": collection, "stac": stac}),
                    )
                    logger.info("Published to Redis")

                if getenv("HTTP_PUBLISH_TO_STAC_API") is not None and getenv(
                        "HTTP_PUBLISH_TO_STAC_API").lower() == "true":
                    try:
                        logger.info("Publishing to STAC API")
                        publish_to_stac_fastapi(stac, collection)
                        logger.info("Published to STAC API")
                    except Exception as e:
                        logger.error(f"Error publishing to STAC API: {e}")
                        break
                if _CLEANUP_DOWNLOADED_FILES:
                    files_to_delete = item_dict.get("files_converted_to_cog", []) + item_dict.get("discovered_files",
                                                                                                  []) + item_dict.get(
                        "files", [])
                    files_to_delete = list(set(files_to_delete))
                    blob_mapping_utility.cleanup_files()

                    for file in files_to_delete:
                        path_to_delete = blob_mapping_utility.get_mounted_filepath_from_url(file)
                        try:
                            os.remove(path_to_delete)
                        except:
                            pass

                logger.info("Done creating STAC item")
                logger.info("Timing end")

        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            break

        # not catching this makes it eaiser to debug, as this exception is raised any of the functions and in the try
        # block fail subfunctions in the try block fail except Exception as e: logger.error(f"Error processing item:

        # except Exception as e:
        #     logger.error(f"Error processing item: {e}")
