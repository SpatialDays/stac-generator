import json
from fastapi.testclient import TestClient

from app.main import app
from app.stac.models import GenerateSTACPayload
from app.stac.services.stac_item_creator import STACItemCreator

client = TestClient(app)
STATUS_ENDPOINT = "/status"


def test_status():

    """
    Tests if the stac get request is successful
    """

    response = client.get(STATUS_ENDPOINT)
    assert response.status_code == 200


def test_create_item():
    with open("app/tests/data/example_gdal_info.json") as file:
        gdal_info_dict = json.load(file)

    mock_item_dict = {
        "gdalInfos": [
            {
                "tiffUrl": "https://path-to-cloud-storage.com/first-file.tif",
                "gdalInfo": gdal_info_dict,
            },
            {
                "tiffUrl": "https://path-to-cloud-storage.com/second-file.tif",
                "gdalInfo": gdal_info_dict,
            },
        ],
        "assets": [
            "https://path-to-cloud-storage.com/readme.md",
            "https://path-to-cloud-storage.com/license.txt",
            "https://path-to-cloud-storage.com/shapefile.shp",
            "https://path-to-cloud-storage.com/metadata.json",
            "https://path-to-cloud-storage.com/first-file.tif",
            "https://path-to-cloud-storage.com/second-file.tif",
        ],
        "method": "POST",
    }

    item = GenerateSTACPayload(**mock_item_dict)

    stac_item_creator = STACItemCreator(item.dict())
    stac_item = stac_item_creator.create_item()

    assert stac_item.id == "test-item"
