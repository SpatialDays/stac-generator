import datetime
import os
import uuid

import logging

logger = logging.getLogger(__name__)

import rasterio
import rio_stac
from pystac import Asset, Item

from .file_operations import (
    get_file_type,
    is_tiff,
    get_mounted_file,
    return_tiff_media_type,
    return_asset_name,
)
from .metadata_parsers.metadata_parser_manager import MetadataParserManager
from .metadata_parsers.utils import merge_stac_items
from ..models import GenerateSTACPayload
from app.stac.services.blob_mounting.blob_mapping_utility import blob_mapping_utility

DOWNLOAD_ASSETS_FROM_URLS = os.getenv("DOWNLOAD_ASSETS_FROM_URLS", "false").lower() == "true"


class STACItemCreator:
    """
    This class is responsible for creating STAC items from dictionaries.

    Attributes:
        payload (GenerateSTACPayload): The input data for creating a STAC item.
        item (Item): The STAC item being created.
        generated_rio_stac_items (list): List of generated items using the rio_stac package.
    """

    def __init__(self, payload: dict):
        """
        Initialize with a dictionary that describes a STAC item.

        Args:
            payload (dict): A dictionary containing the necessary data to create a STAC item.
        """
        logger.info(f"Initializing STAC item creator")
        if not isinstance(payload, dict):
            raise ValueError("Payload should be a dictionary.")
        self.payload = GenerateSTACPayload(**payload)
        self.item = Item(
            id=str(uuid.uuid4()),
            geometry=None,
            bbox=None,
            datetime=datetime.datetime.now(),
            properties={},
        )
        self.generated_rio_stac_items = []
        logger.info(f"Initialized STAC item creator")

    def create_item(self) -> Item:
        """
        Create a STAC Item from the provided dictionary.

        Returns:
            Item: The created STAC item.
        """
        logger.info(f"Creating STAC item from payload")
        self._add_assets()
        self._add_tiff_stac_metadata()

        if self.payload.parser and self.payload.metadata:
            self._add_parsed_metadata(
                metadata_type=self.payload.parser,
                metadata=self.payload.metadata,
                metadata_url=self.payload.metadata_url,
            )
        logger.info(f"Created STAC item")
        return self.item.to_dict()

    def _add_assets(self):
        """
        Add assets to the STAC item from the file paths provided in the payload.
        """
        logger.info(f"Adding assets to STAC item from payload")
        parser = MetadataParserManager.get_parser(self.payload.parser)

        for file in self.payload.files:
            if not is_tiff(file):
                filename = return_asset_name(file)
                if hasattr(parser, 'get_asset_common_name_from_filename'):
                    asset_key = parser.get_asset_common_name_from_filename(return_asset_name(filename))
                else:
                    asset_key = return_asset_name(filename)
                media_type = get_file_type(file)
                if asset_key.lower() == "rendered_preview":
                    asset = Asset(href=file, media_type=media_type, roles=["overview"],
                                  extra_fields={"rel": "preview", "title": "Rendered preview"})
                else:
                    asset = Asset(href=file, media_type=media_type)
                self.item.add_asset(key=asset_key, asset=asset)
        logger.info(f"Added assets to STAC item")

    def _generate_and_add_metadata(self, filepath, add_asset=True):
        """
        Generate STAC metadata for the given TIFF file using rio_stac and add to the STAC item.
        """
        if DOWNLOAD_ASSETS_FROM_URLS:
            try:
                blob_mapping_utility.download_blob(filepath)
            except Exception as e:
                logger.debug(f"File {filepath} could not be downloaded. Probably not part of a storage account.")

        parser = MetadataParserManager.get_parser(self.payload.parser)
        logger.info(f"Generating metadata for {filepath} using {parser}")
        generated_stac = rio_stac.create_stac_item(
            get_mounted_file(filepath),
            with_eo=True,
            with_proj=True,
            with_raster=True,
            geom_densify_pts=21,
        )
        logger.info(f"Generated metadata for {filepath} using {parser}")
        logger.info(f"Adding metadata for {filepath} using {parser} to STAC item")
        self.generated_rio_stac_items.append(generated_stac)
        logger.info(f"Added metadata into generated_rio_stac_items for {filepath} using {parser}")

        if add_asset:
            logger.info(f"Adding asset for {filepath} using {parser} to STAC item")
            if hasattr(parser, 'get_asset_common_name_from_filename'):
                asset_key = parser.get_asset_common_name_from_filename(return_asset_name(filepath))
                logger.info(f"Got asset key {asset_key} for {filepath} using {parser} to STAC item")
            else:
                asset_key = return_asset_name(filepath)
                logger.info(
                    f"Could not get asset key for {filepath} using {parser} to STAC item, using filename {asset_key} as asset key")

            generated_stac.assets["asset"].media_type = return_tiff_media_type(filepath)
            generated_stac.assets["asset"].href = filepath
            logger.info(f"Adding asset to stac record for {filepath} using {parser} to STAC item")
            self.item.add_asset(
                key=asset_key, asset=generated_stac.assets["asset"]
            )
            logger.info(f"Added asset to stac record for {filepath} using {parser} to STAC item")
        logger.info(f"Added metadata for {filepath} using {parser} to STAC item")
        return generated_stac

    def _add_tiff_stac_metadata(self):
        """
        Generate STAC metadata for each TIFF file using rio_stac, and add to the STAC item.
        """
        logger.info(f"Adding TIFF STAC metadata to STAC item from payload")
        tiff_filepath = None
        for filepath in self.payload.files:
            if is_tiff(filepath):
                generated_item = self._generate_and_add_metadata(filepath)
                tiff_filepath = filepath

        if not self.generated_rio_stac_items:
            raise ValueError("No rio_stac generated items found.")

        self.item.properties.update(generated_item.properties)
        self.item.bbox = generated_item.bbox
        self.item.geometry = generated_item.geometry
        self.item.stac_extensions = generated_item.stac_extensions

        if tiff_filepath:
            logger.info(f"Opening {tiff_filepath} to get TIFFTAG_DATETIME")
            with rasterio.open(get_mounted_file(tiff_filepath)) as ds:
                tags = ds.tags()
                tag_datetime = tags.get("TIFFTAG_DATETIME")  # 2022:09:09 15:27:53
                if tag_datetime is not None:
                    self.item.datetime = datetime.datetime.strptime(
                        tag_datetime, "%Y:%m:%d %H:%M:%S"
                    )

                self.item.properties["license"] = os.getenv(
                    "STAC_LICENSE_TYPE", "proprietary"
                )

                tag_resolution = ds.res
                if tag_resolution is not None:
                    self.item.properties["gsd"] = tag_resolution[0]
            logger.info(f"Closed {tiff_filepath}")

    def _add_parsed_metadata(self, metadata_type, metadata, metadata_url=None):
        """
        Parse the metadata using the appropriate parser and add it to the STAC item.
        """
        # Using MetadataParserManager to get the appropriate parser
        parser = MetadataParserManager.get_parser(metadata_type)

        # Optional metadata_url can be provided to the parser
        if metadata_url:
            metadata_stac_item = parser.parse(metadata, metadata_url=metadata_url)
        else:
            metadata_stac_item = parser.parse(metadata)

        # Now merge the metadata_stac_item into the item
        self.item = Item.from_dict(
            merge_stac_items(self.item.to_dict(), metadata_stac_item)
        )
