# poetry run python -m pytest --log-level=INFO --capture=no

from fastapi.testclient import TestClient
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
    """

    logger.info("Testing status endpoint")

    response = client.get(STATUS_ROUTE)
    assert response.status_code == 200


def test_create_item():
    """
    Tests is the create item request is successful
    """
    mock_item_dict = {
        "files": [
            "https://path-to-cloud-storage.com/readme.md",
            "https://path-to-cloud-storage.com/license.txt",
            "https://path-to-cloud-storage.com/shapefile.shp",
            "manual-upload-storage-blob/017078204010_01_20AUG12110524-S3DS-017078204010_01_P001.TIF",
        ],
    }

    logger.info("Testing create item endpoint")

    response = client.post(STAC_ROUTE + GENERATE_STAC_ENDPOINT, json=mock_item_dict)
    assert response.status_code == 200
