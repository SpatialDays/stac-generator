from pystac import Asset, Item, Provider, MediaType
from ..models import GenerateSTACPayload
from loguru import logger
import datetime


class STACItemCreator:
    """
    This class is responsible for creating STAC items from dictionaries.
    """

    def __init__(self, item_dict: dict):
        """
        Initialize with a dictionary that describes a STAC item.

        Args:
            item_dict (dict): A dictionary containing the necessary data to create a STAC item.
        """
        self.item_data = GenerateSTACPayload(**item_dict)

    def create_item(self) -> Item:
        """
        Create a STAC Item from the provided dictionary.

        Returns:
            Item: The created STAC item.
        """
        return None
