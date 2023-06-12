# `poetry run python -m pytest --log-level=INFO --capture=no` or if in docker do `docker exec -it 8d poetry run poetry run python -m pytest --log-level=INFO --capture=no`

from fastapi.testclient import TestClient

import redis
import json
import os
from loguru import logger

from app.main import app

logger.add("app/tests/test_stac.log", rotation="10 MB")

client = TestClient(app)

STATUS_ROUTE = "/status"
STAC_ROUTE = "/stac"
GENERATE_STAC_ENDPOINT = "/generate"


def test_status():
    """
    Tests if the status request is successful

    poetry run python -m pytest --log-level=INFO --capture=no app/tests/test_stac.py::test_status
    """
    response = client.get(STATUS_ROUTE)
    assert response.status_code == 200


def test_create_item():
    """
    Tests is the create item request is successful

    poetry run python -m pytest --log-level=INFO --capture=no app/tests/test_stac.py::test_create_item
    """
    mock_item_dict = {
        "files": [
            "https://path-to-cloud-storage.com/readme.md",
            "https://path-to-cloud-storage.com/license.txt",
            "https://path-to-cloud-storage.com/shapefile.shp",
            "manual-upload-storage-blob/017078204010_01_20AUG12110524-S3DS-017078204010_01_P001.TIF",  # This should be your own file
        ],
        "metadata": {
            "ID": "017078204010_01_20AUG12110524-S3DS-017078204010_01_P001",
        },
        "parser": "example",
    }
    response = client.post(STAC_ROUTE + GENERATE_STAC_ENDPOINT, json=mock_item_dict)
    assert response.status_code == 200


def test_redis_create_item():
    """
    Tests if the item can be added to a Redis list

    poetry run python -m pytest --log-level=INFO --capture=no app/tests/test_stac.py::test_redis_create_item

    """
    redis_client = redis.StrictRedis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=os.getenv("REDIS_DB"),
        decode_responses=True,
    )

    # Specify the key and the payload to be pushed
    key = "stac_generator_generate"
    mock_item_dict = {
        "files": [
            "https://somestorageaccount.blob.core.windows.net/somecontainer/folder_path/license.txt",
            "manual-upload-storage-blob/017078204010_01_20AUG12110524-S3DS-017078204010_01_P001.TIF",  # This should be your own file
        ],
        "metadata": {
            "ID": "017078204010_01_20AUG12110524-S3DS-017078204010_01_P001",
        },
        "parser": "example",
    }

    payload = json.dumps(mock_item_dict)
    redis_client.rpush(key, payload)
    logger.info("Item successfully added to Redis")
