import json
import mimetypes
import os
from typing import Union, Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

import pathlib

import rasterio
from rasterio.env import GDALVersion

DOWNLOAD_ASSETS_FROM_URLS = os.getenv("DOWNLOAD_ASSETS_FROM_URLS", "false").lower() == "true"
from app.stac.services.blob_mounting.blob_mapping_utility import blob_mapping_utility


def get_file_type(filepath: str):
    """
    Determines the MIME type of a file based on its content.

    Args:
        filepath (str): The path to the file.

    Returns:
        str: The MIME type of the file.
    """
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type


def is_tiff(filepath: str):
    """
    Determines if a file is a TIFF based on its MIME type.

    Args:
        filepath (str): The path to the file.

    Returns:
        bool: True if the file is a TIFF, False otherwise.
    """
    mime_type = get_file_type(filepath)
    return mime_type == "image/tiff"


def get_mounted_file(filepath: str):
    """
    Converts a given file path into its corresponding path within a mounted file system.

    This function parses the given file path and prepends it with '/mnt/' to simulate a path
    in a file system that's been mounted at '/mnt/'.

    Args:
        filepath (str): The original file path.

    Returns:
        str: The corresponding path in the mounted file system.
    """
    if DOWNLOAD_ASSETS_FROM_URLS:
        return blob_mapping_utility.get_mounted_filepath_from_url(filepath)
    return filepath


def is_cog(
    src_path: Union[str, pathlib.PurePath],
    strict: bool = False,
) -> Tuple[bool, List[str], List[str]]:
    """
    Validate Cloud Optimized Geotiff.
    This script is the rasterio equivalent of
    https://svn.osgeo.org/gdal/trunk/gdal/swig/python/samples/validate_cloud_optimized_geotiff.py
    Parameters
    ----------
    src_path: str or PathLike object
        A dataset path or URL. Will be opened in "r" mode.
    strict: bool
        Treat warnings as errors
    Returns
    -------
    is_valid: bool
        True is src_path is a valid COG.
    errors: list
        List of validation errors.
    warnings: list
        List of validation warnings.
    """
    errors: List[str] = []
    warnings: List[str] = []
    details: Dict[str, Any] = {}

    if not GDALVersion.runtime().at_least("2.2"):
        raise Exception("GDAL 2.2 or above required")

    with rasterio.Env():
        with rasterio.open(src_path) as src:
            if not src.driver == "GTiff":
                errors.append("The file is not a GeoTIFF")
                return False, errors, warnings

            if any(pathlib.Path(x).suffix.lower() == ".ovr" for x in src.files):
                errors.append(
                    "Overviews found in external .ovr file. They should be internal"
                )

            overviews = src.overviews(1)
            if src.width > 512 and src.height > 512:
                if not src.is_tiled:
                    errors.append(
                        "The file is greater than 512xH or 512xW, but is not tiled"
                    )

                if not overviews:
                    warnings.append(
                        "The file is greater than 512xH or 512xW, it is recommended "
                        "to include internal overviews"
                    )

            ifd_offset = int(src.get_tag_item("IFD_OFFSET", "TIFF", bidx=1))
            if ifd_offset > 300:
                errors.append(
                    f"The offset of the main IFD should be < 300. It is {ifd_offset} instead"
                )

            ifd_offsets = [ifd_offset]
            details["ifd_offsets"] = {}
            details["ifd_offsets"]["main"] = ifd_offset

            if overviews and overviews != sorted(overviews):
                errors.append("Overviews should be sorted")

            for ix, dec in enumerate(overviews):
                if not dec > 1:
                    errors.append(
                        "Invalid Decimation {} for overview level {}".format(dec, ix)
                    )

                # Check that the IFD of descending overviews are sorted by increasing
                # offsets
                ifd_offset = int(src.get_tag_item("IFD_OFFSET", "TIFF", bidx=1, ovr=ix))
                ifd_offsets.append(ifd_offset)

                details["ifd_offsets"]["overview_{}".format(ix)] = ifd_offset
                if ifd_offsets[-1] < ifd_offsets[-2]:
                    if ix == 0:
                        errors.append(
                            "The offset of the IFD for overview of index {} is {}, "
                            "whereas it should be greater than the one of the main "
                            "image, which is at byte {}".format(
                                ix, ifd_offsets[-1], ifd_offsets[-2]
                            )
                        )
                    else:
                        errors.append(
                            "The offset of the IFD for overview of index {} is {}, "
                            "whereas it should be greater than the one of index {}, "
                            "which is at byte {}".format(
                                ix, ifd_offsets[-1], ix - 1, ifd_offsets[-2]
                            )
                        )

            block_offset = src.get_tag_item("BLOCK_OFFSET_0_0", "TIFF", bidx=1)

            data_offset = int(block_offset) if block_offset else 0
            data_offsets = [data_offset]
            details["data_offsets"] = {}
            details["data_offsets"]["main"] = data_offset

            for ix, _dec in enumerate(overviews):
                block_offset = src.get_tag_item(
                    "BLOCK_OFFSET_0_0", "TIFF", bidx=1, ovr=ix
                )
                data_offset = int(block_offset) if block_offset else 0
                data_offsets.append(data_offset)
                details["data_offsets"]["overview_{}".format(ix)] = data_offset

            if data_offsets[-1] != 0 and data_offsets[-1] < ifd_offsets[-1]:
                if len(overviews) > 0:
                    errors.append(
                        "The offset of the first block of the smallest overview "
                        "should be after its IFD"
                    )
                else:
                    errors.append(
                        "The offset of the first block of the image should "
                        "be after its IFD"
                    )

            for i in range(len(data_offsets) - 2, 0, -1):
                if data_offsets[i] < data_offsets[i + 1]:
                    errors.append(
                        "The offset of the first block of overview of index {} should "
                        "be after the one of the overview of index {}".format(i - 1, i)
                    )

            if len(data_offsets) >= 2 and data_offsets[0] < data_offsets[1]:
                errors.append(
                    "The offset of the first block of the main resolution image "
                    "should be after the one of the overview of index {}".format(
                        len(overviews) - 1
                    )
                )

        for ix, _dec in enumerate(overviews):
            with rasterio.open(src_path, OVERVIEW_LEVEL=ix) as ovr_dst:
                if ovr_dst.width > 512 and ovr_dst.height > 512:
                    if not ovr_dst.is_tiled:
                        errors.append("Overview of index {} is not tiled".format(ix))

    is_valid = False if errors or (warnings and strict) else True

    return is_valid, errors, warnings


def return_tiff_media_type(tiff_path: str) -> str:
    """Return the media type of a TIFF file

    Args:
        tiff_path (str): Path to the TIFF file

    Returns:
        str: The media type of the TIFF file
    """
    if os.getenv("CHECK_COG_TYPE").lower() == "true":
        cog = is_cog(get_mounted_file(tiff_path))

        if os.getenv("LOG_COG_INFO").lower() == "true":
            logger.info("Is the file a COG: {}".format(cog[0]))

            if len(cog[1]) > 0:
                logger.info("COG errors: {}".format(cog[1]))

            if len(cog[2]) > 0:
                logger.info("COG warnings: {}".format(cog[2]))

        if cog[0]:
            return "image/tiff; application=geotiff; profile=cloud-optimized"

    return "image/tiff; application=geotiff"


def return_asset_name(filename: str, include_extension: bool = True) -> str:
    """Return the asset name of a file

    Args:
        filename (str): The filename
        include_extension (bool, optional): Whether to include the extension in the asset name. Defaults to True.

    Returns:
        str: The asset name
    """
    if include_extension:
        return os.path.basename(filename)

    return os.path.splitext(os.path.basename(filename))[0]


def return_asset_href(filepath):
    if DOWNLOAD_ASSETS_FROM_URLS:
        return blob_mapping_utility.get_url_from_mounted_filepath(filepath)
    return filepath
