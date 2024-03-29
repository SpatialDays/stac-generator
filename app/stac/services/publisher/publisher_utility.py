import json
import os
import time
import requests
import logging

logger = logging.getLogger(__name__)


def publish_to_stac_fastapi(stac, collection, max_retries=5, retry_delay=5) -> str:
    """
    Publish data to a STAC FastAPI.

    This function sends data to a STAC FastAPI service. If the item does not exist,
    it performs a POST to the /items/ endpoint. If it does exist, it performs a PUT
    to the /items/{id} endpoint.

    :param stac: The data to be published.
    :param collection: The collection where the data belongs.
    :param max_retries: Maximum number of retries in case of a DB lock error.
    :param retry_delay: Delay between retries in seconds.
    :return: True if successful, False otherwise.

    :raises ValueError: If STAC_API_URL environment variable is not set.
    :raises Exception: If max_retries is reached or if there is an error.
    :raises requests.RequestException: If there is a request error.
    """
    stac_api_url = os.getenv("STAC_API_URL", None)

    # Check if environment variables are set
    if not stac_api_url:
        logger.error("STAC_API_URL environment variable is not set.")
        raise ValueError("STAC_API_URL environment variable is not set.")

    item_id = stac["id"]
    item_url = f"{stac_api_url}/collections/{collection}/items/{item_id}"
    logger.info(f"Publishing to {item_url}")

    for _ in range(max_retries):
        try:
            # Attempt POST request
            response = requests.post(
                f"{stac_api_url}/collections/{collection}/items",
                data=json.dumps(stac),
                headers={"Content-Type": "application/json"},
            )

            # If POST fails, attempt PUT request
            if (
                    response.status_code == 409
            ):  # Assuming 409 Conflict indicates item already exists
                response = requests.put(
                    item_url,
                    data=json.dumps(stac),
                    headers={"Content-Type": "application/json"},
                )

            # Check if successful
            if response.status_code in [200, 201]:
                return item_url
            else:
                logger.warning("DB is locked, retrying...")
                time.sleep(retry_delay)
                continue


        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            raise e
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e

    logger.error("Max retries reached. Giving up.")
    raise Exception("Max retries reached. Giving up.")
