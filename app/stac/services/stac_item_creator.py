from pystac import Asset, Item, Provider, MediaType
from ..models import GenerateSTACPayload
from loguru import logger
import datetime
import json
from .utils import get_file_type


class STACItemCreator:
    """
    This class is responsible for creating STAC items from dictionaries.
    """

    def __init__(self, payload: dict):
        """
        Initialize with a dictionary that describes a STAC item.

        Args:
            item_dict (dict): A dictionary containing the necessary data to create a STAC item.
        """
        self.payload = GenerateSTACPayload(**payload)
        self.item = None

    def create_item(self) -> Item:
        """
        Create a STAC Item from the provided dictionary.

        Returns:
            Item: The created STAC item.
        """
        # Initialize the STAC item
        self.item = Item(
            id="test-id",
            geometry=None,
            bbox=None,
            datetime=datetime.datetime.now(),
            properties={},
        )

        # Add the assets
        self._add_assets()

        # Log this with indentation to make it easier to read
        logger.info(json.dumps(self.item.to_dict(), indent=4))
        return self.item.to_dict()

    def _add_assets(self):
        for file in self.payload.files:
            media_type = get_file_type(file)
            asset = Asset(href=file, media_type=media_type)
            self.item.add_asset(key=file, asset=asset)
