import json
import os
import time
import requests
import pystac
from loguru import logger


def publish_to_stac_fastapi(stac, collection, max_retries=5, retry_delay=1):
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
    """
    stac_api_url = os.getenv("STAC_API_URL")
    publish_to_stac_api = os.getenv("PUBLISH_TO_STAC_API")

    # Check if environment variables are set
    if not stac_api_url:
        logger.error("STAC_API_URL environment variable is not set.")
        return False

    if publish_to_stac_api:
        item_id = stac["id"]
        item_url = f"{stac_api_url}/collections/{collection}/items/{item_id}"

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
                    return f"{stac_api_url}/collections/{collection}/items/{item_id}"
                elif "DB lock error" in response.text: # TODO: What's the response code for a DB lock error?
                    logger.warning("DB is locked, retrying...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Failed to publish to STAC API: {response.content}")
                    return False

            except requests.RequestException as e:
                logger.error(f"Request error: {e}")
                return False
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                return False

        logger.error("Max retries reached. Giving up.")
        return False

    return True
