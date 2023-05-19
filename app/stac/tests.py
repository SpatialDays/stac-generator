# Run with python -m unittest app.stac.tests

import unittest
from loguru import logger
from .models import GenerateSTACPayload
from .tasks import create_item


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

        self.assertEqual(create_item(mock_item_dict), expected_result)


if __name__ == "__main__":
    unittest.main()
