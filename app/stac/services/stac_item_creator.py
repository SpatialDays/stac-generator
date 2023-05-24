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
from .utils import get_file_type, is_tiff


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
        self.generated_rio_stac_items = []
        self.combined_tiff = None

    def create_item(self) -> Item:
        """
        Create a STAC Item from the provided dictionary.

        Returns:
            Item: The created STAC item.
        """

        # self._combine_tiffs() # TODO: Make this optional and add a flag to the payload
        self._add_assets()
        self._add_rio_stac_metadata()
        self._add_gdal_metadata()

        with open("data/item.json", "w") as f:
            json.dump(self.item.to_dict(), f, indent=2)

        return self.item.to_dict()

    def _add_assets(self):
        for file in self.payload.files:
            if not is_tiff(file):
                media_type = get_file_type(file)
                asset = Asset(href=file, media_type=media_type)
                self.item.add_asset(key=file, asset=asset)

    def _add_gdal_metadata(self):
        for gdal_metadata in self.payload.gdalInfos:
            info = gdal_metadata.gdalInfo
            gdal_metadata = info["metadata"]
            gdal_datetime = gdal_metadata[""]["TIFFTAG_DATETIME"]  # 2022:09:09 15:27:53
            gdal_datetime = datetime.datetime.strptime(
                gdal_datetime, "%Y:%m:%d %H:%M:%S"
            )

            self.item.datetime = gdal_datetime
            self.item.properties["license"] = gdal_metadata[""]["TIFFTAG_COPYRIGHT"]

    def _combine_tiffs(self):
        datasets = []
        for filepath in self.payload.files:
            if is_tiff(filepath):
                ds = rxr.open_rasterio(filepath, masked=True)
                datasets.append(ds)

        # Merge the data
        combined = xr.concat(datasets, dim="band")
        combined.rio.to_raster("combined.tif")

        return "combined.tif"

    def _add_rio_stac_metadata(self):
        # Generate the stac metadata for each tiff file
        for filepath in self.payload.files:
            if is_tiff(filepath):
                generated_stac = rio_stac.create_stac_item(
                    filepath,
                    with_eo=True,
                    with_proj=True,
                    with_raster=True,
                    geom_densify_pts=21,
                )
                self.generated_rio_stac_items.append(generated_stac)

                self.item.add_asset(key=filepath, asset=generated_stac.assets["asset"])

        self.item.properties = {
            **self.item.properties,
            **self.generated_rio_stac_items[0].properties,
        }
        self.item.bbox = self.generated_rio_stac_items[0].bbox
        self.item.geometry = self.generated_rio_stac_items[0].geometry
        self.item.stac_extensions = self.generated_rio_stac_items[0].stac_extensions
