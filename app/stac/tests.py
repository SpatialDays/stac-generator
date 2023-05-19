# Run with python -m unittest app.stac.tests

import unittest
from loguru import logger
from .models import GenerateSTACPayload
from .services.stac_item_creator import STACItemCreator


class TestTasks(unittest.TestCase):
    def test_create_item(self):
        mock_item_dict = {
            "source": "manual",
            "provider": "Spatial Days",
            "collection": "test-collection",
            "itemId": "test-item",
            "assetPaths": ["data/Maxar/test-item.tif"],
            "metadataPaths": ["data/Maxar/metadata.json"],
        }
        item = GenerateSTACPayload(**mock_item_dict)

        expected_result = {
            "message": "STAC Item created",
        }

        stac_item_creator = STACItemCreator(item.dict())
        stac_item = stac_item_creator.create_item()

        self.assertEqual(stac_item.id, "test-item")


if __name__ == "__main__":
    unittest.main()
