import datetime
import os
import uuid

import rioxarray as rxr
import xarray as xr
import rasterio

from pystac import Asset, Item
import rio_stac
from ..models import GenerateSTACPayload
from .file_operations import (
    get_file_type,
    is_tiff,
    get_mounted_file,
    return_tiff_media_type,
)

from loguru import logger

from .metadata_parsers.metadata_parser_manager import MetadataParserManager
from .metadata_parsers.utils import merge_stac_items


class STACItemCreator:
    """
    This class is responsible for creating STAC items from dictionaries.

    Attributes:
        payload (GenerateSTACPayload): The input data for creating a STAC item.
        item (Item): The STAC item being created.
        generated_rio_stac_items (list): List of generated items using the rio_stac package.
        combined_tiff (str): Path to the combined TIFF file from all input TIFF files.
    """

    def __init__(self, payload: dict):
        """
        Initialize with a dictionary that describes a STAC item.

        Args:
            payload (dict): A dictionary containing the necessary data to create a STAC item.
        """
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
        self.combined_tiff = None

    def create_item(self) -> Item:
        """
        Create a STAC Item from the provided dictionary.

        Returns:
            Item: The created STAC item.
        """
        self._add_assets()

        if os.environ.get("MERGE_TIFFS", False).lower() == "true":
            self.combined_tiff = self._combine_tiffs()

        self._add_tiff_stac_metadata()

        if self.payload.parser and self.payload.metadata:
            self._add_parsed_metadata(
                metadata_type=self.payload.parser, metadata=self.payload.metadata
            )

        logger.info(f"Created STAC item: {self.item.to_dict()}")

        return self.item.to_dict()

    def _add_assets(self):
        """
        Add assets to the STAC item from the file paths provided in the payload.
        """
        for file in self.payload.files:
            if not is_tiff(file):
                media_type = get_file_type(file)
                asset = Asset(href=file, media_type=media_type)
                self.item.add_asset(key=file, asset=asset)

    def _combine_tiffs(self):
        """
        Combine all TIFF files provided in the payload into a single TIFF file.

        Note: The merging operation may have limitations and potential issues.
        Please be aware that the resulting merged TIFF file may not always be
        perfect or desirable.
        """
        datasets = []
        for filepath in self.payload.files:
            if is_tiff(filepath):
                ds = rxr.open_rasterio(get_mounted_file(filepath), masked=True)
                datasets.append(ds)

        # Merge the data
        combined = xr.concat(datasets, dim="band")
        combined.rio.to_raster("combined.tif")

        return "combined.tif"

    def _generate_and_add_metadata(self, filepath, add_asset=True):
        """
        Generate STAC metadata for the given TIFF file using rio_stac and add to the STAC item.
        """
        generated_stac = rio_stac.create_stac_item(
            get_mounted_file(filepath),
            with_eo=True,
            with_proj=True,
            with_raster=True,
            geom_densify_pts=21,
        )
        self.generated_rio_stac_items.append(generated_stac)

        if add_asset:
            generated_stac.assets["asset"].media_type = return_tiff_media_type(filepath)
            self.item.add_asset(key=filepath, asset=generated_stac.assets["asset"])

        return generated_stac

    def _add_tiff_stac_metadata(self):
        """
        Generate STAC metadata for each TIFF file using rio_stac, and add to the STAC item.
        """
        for filepath in self.payload.files:
            if is_tiff(filepath):
                generated_item = self._generate_and_add_metadata(filepath)

        if self.combined_tiff:
            generated_item = self._generate_and_add_metadata(
                self.combined_tiff, add_asset=False
            )

        if not self.generated_rio_stac_items:
            raise ValueError("No rio_stac generated items found.")

        self.item.properties.update(generated_item.properties)
        self.item.bbox = generated_item.bbox
        self.item.geometry = generated_item.geometry
        self.item.stac_extensions = generated_item.stac_extensions

        with rasterio.open(get_mounted_file(filepath)) as ds:
            tags = ds.tags()
            tag_datetime = tags.get("TIFFTAG_DATETIME")  # 2022:09:09 15:27:53
            if tag_datetime is not None:
                self.item.datetime = datetime.datetime.strptime(
                    tag_datetime, "%Y:%m:%d %H:%M:%S"
                )

            tag_copyright = tags.get("TIFFTAG_COPYRIGHT")
            if tag_copyright is not None:
                self.item.properties["license"] = tag_copyright

            tag_resolution = ds.res
            if tag_resolution is not None:
                self.item.properties["gsd"] = tag_resolution[0]

    def _add_parsed_metadata(self, metadata_type, metadata):
        """
        Parse the metadata using the appropriate parser and add it to the STAC item.
        """
        # Using MetadataParserManager to get the appropriate parser
        parser = MetadataParserManager.get_parser(metadata_type)
        metadata_stac_item = parser.parse(metadata)

        # Now merge the metadata_stac_item into the item
        self.item = Item.from_dict(
            merge_stac_items(self.item.to_dict(), metadata_stac_item)
        )
