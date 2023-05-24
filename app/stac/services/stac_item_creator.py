import datetime
import json

import rasterio
import rioxarray as rxr
import xarray as xr

import numpy as np
from loguru import logger
from pystac import Asset, Item, Provider, MediaType
import rio_stac
from ..models import GenerateSTACPayload
from .utils import get_file_type, is_tiff, merge_rio_stac_items


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
        self.item = Item(
            id="test-id",
            geometry=None,
            bbox=None,
            datetime=datetime.datetime.now(),
            properties={},
        )
        self.combined_tiff = None

    def create_item(self) -> Item:
        """
        Create a STAC Item from the provided dictionary.

        Returns:
            Item: The created STAC item.
        """
        # Add the assets
        # self._combine_tiffs() # Make this optional
        self._add_assets()
        self._add_rio_stac_metadata()
        self._add_gdal_metadata()

        print(self.item.to_dict())

        return self.item.to_dict()

    def _add_assets(self):
        for file in self.payload.files:
            media_type = get_file_type(file)
            asset = Asset(href=file, media_type=media_type)
            self.item.add_asset(key=file, asset=asset)

    def _add_gdal_metadata(self):
        # for gdal_metadata in self.payload.gdalInfos:
        #     url, info = gdal_metadata.tiffUrl, gdal_metadata.gdalInfo
        #     self.item.properties = {**self.item.properties, **info.get("stac", {})}
        pass

    # TODO: Make this optional and add a flag to the payload
    def _combine_tiffs(self):
        # Create a list for the data
        datasets = []
        # Check each file in the list
        for filepath in self.payload.files:
            if is_tiff(filepath):
                # Open the file
                ds = rxr.open_rasterio(filepath, masked=True)
                # Add the data to the list
                datasets.append(ds)

        # Merge the data
        combined = xr.concat(datasets, dim="band")

        # Write the combined raster to a new file
        combined.rio.to_raster("combined.tif")

        return "combined.tif"

    def _add_rio_stac_metadata(self):
        # Generate the stac metadata for each tiff file
        generated_rio_stac_items = []
        for filepath in self.payload.files:
            if is_tiff(filepath):
                generated_stac = rio_stac.create_stac_item(
                    filepath,
                    with_eo=True,
                    with_proj=True,
                    with_raster=True,
                    geom_densify_pts=21,
                )
                generated_rio_stac_items.append(generated_stac)

        # Now we want to add the merged rio stac item to the self.item
        self.item.properties = {
            **self.item.properties,
            **generated_rio_stac_items[0].properties,
        }
        self.item.bbox = generated_rio_stac_items[0].bbox
        self.item.geometry = generated_rio_stac_items[0].geometry
        self.item.stac_extensions = generated_rio_stac_items[0].stac_extensions
