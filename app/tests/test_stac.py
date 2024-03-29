# `poetry run python -m pytest --log-level=INFO --capture=no` or if in docker do `docker exec -it 8d poetry run poetry run python -m pytest --log-level=INFO --capture=no`

from fastapi.testclient import TestClient

import logging
logger = logging.getLogger(__name__)

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
            "https://path-to-storage.com/readme.md",
            "https://path-to-storage.com/shapefile.shp",
            "https://deafrica-sentinel-1.s3.af-south-1.amazonaws.com/s1_rtc/N13E025/2018/01/04/0101B0/s1_rtc_0101B0_N13E025_2018_01_04_ANGLE.tif",
        ],
        "metadata": {"ID": "example_stac_item"},
        "metadata_url": "https://path-to-storage.com/SX8888.json",
        "parser": "example",
    }
    response = client.post(STAC_ROUTE + GENERATE_STAC_ENDPOINT, json=mock_item_dict)
    assert response.status_code == 200

