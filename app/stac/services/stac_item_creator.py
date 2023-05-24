import datetime
import random

import rioxarray as rxr
import xarray as xr

from pystac import Asset, Item
import rio_stac
from ..models import GenerateSTACPayload
from .utils import get_file_type, is_tiff


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
            id=f"item-{random.randint(0, 100000)}",
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
        self._add_rio_stac_metadata()
        self._add_gdal_metadata()

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

    def _add_gdal_metadata(self):
        """
        Add GDAL metadata to the STAC item from the gdalInfos provided in the payload.
        """
        for gdal_metadata in self.payload.gdalInfos:
            try:
                info = gdal_metadata.gdalInfo
                metadata = info.get("metadata")
                if metadata is None:
                    continue
                gdal_datetime = metadata[""]["TIFFTAG_DATETIME"]  # 2022:09:09 15:27:53
                self.item.datetime = datetime.datetime.strptime(
                    gdal_datetime, "%Y:%m:%d %H:%M:%S"
                )
                gdal_copyright = metadata[""]["TIFFTAG_COPYRIGHT"]
                if gdal_copyright is not None:
                    self.item.properties["license"] = gdal_copyright
            except KeyError:
                raise KeyError("Key error occurred while parsing GDAL metadata.")

    def _combine_tiffs(self):
        """
        Combine all TIFF files provided in the payload into a single TIFF file.
        """
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
        """
        Generate STAC metadata for each TIFF file using rio_stac, and add to the STAC item.
        """
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
                generated_stac.assets[
                    "asset"
                ].media_type = "image/tiff; application=geotiff"  # with cog checker we should add profile=cloud-optimized",
                self.item.add_asset(key=filepath, asset=generated_stac.assets["asset"])

        if not self.generated_rio_stac_items:
            raise ValueError("No rio_stac generated items found.")

        generated_item = self.generated_rio_stac_items[0]
        self.item.properties.update(generated_item.properties)
        self.item.bbox = generated_item.bbox
        self.item.geometry = generated_item.geometry
        self.item.stac_extensions = generated_item.stac_extensions
