from pystac import Asset, Item, Provider, MediaType
from ..models import GenerateSTACPayload
from loguru import logger
from typing import List
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
        logger.info(f"Creating STAC item from {self.item_data}")
        # TODO: Infer the bbox from the assetPaths
        bbox = [-180, -90, 180, 90]

        # TODO: Infer the datetime from the assetPaths / metadataPaths
        datetime_now = datetime.datetime.now()

        stac_item = Item(
            id=self.item_data.itemId,
            geometry=None,
            bbox=bbox,
            datetime=datetime_now,
            properties={},
        )

        stac_item.properties["source"] = self.item_data.source

        self._add_assets_to_item(stac_item)

        # TODO: Add metadata to the item using self.item_data.metadataPaths

        return stac_item

    def _add_assets_to_item(self, stac_item: Item) -> None:
        """
        Add assets to the STAC item.

        Args:
            stac_item (Item): The STAC item to add assets to.
        """
        for asset_path in self.item_data.assetPaths:
            asset = Asset(href=asset_path, media_type=MediaType.GEOTIFF)
            asset_key = "asset"
            stac_item.add_asset(asset_key, asset)

    def add_metadata_to_item(self, stac_item: Item) -> None:
        """
        Add metadata to the STAC item from metadataPaths.

        Args:
            stac_item (Item): The STAC item to add metadata to.
        """
        # TODO: Implement this function

        pass
