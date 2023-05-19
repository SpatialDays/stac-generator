# Run with python -m unittest app.stac.tests

import unittest
from .models import GenerateSTACPayload
from .tasks import create_item
from loguru import logger


class TestTasks(unittest.TestCase):
    def test_create_item(self):
        mock_item_dict = {
            "source": "string",
            "provider": "string",
            "collection": "string",
            "itemId": "string",
            "assetPaths": ["string"],
            "metadataPaths": ["string"],
        }
        item = GenerateSTACPayload(**mock_item_dict)

        expected_result = {
            "message": "STAC Item created",
        }

        self.assertEqual(create_item(mock_item_dict), expected_result)


if __name__ == "__main__":
    unittest.main()
