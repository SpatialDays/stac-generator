import pytest
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
    mock_item_dict = {
        "source": "manual",
        "provider": "Spatial Days",
        "collection": "test-collection",
        "itemId": "test-item",
        "assetPaths": ["data/Maxar/test-item.tif"],
        "metadataPaths": ["data/Maxar/metadata.json"],
    }
    item = GenerateSTACPayload(**mock_item_dict)

    stac_item_creator = STACItemCreator(item.dict())
    stac_item = stac_item_creator.create_item()

    assert stac_item.id == "test-item"
