from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, root_validator
from loguru import logger
import requests


class GenerateSTACPayload(BaseModel):
    files: List[str] = Field(
        ...,
        example=[
            "https://path-to-storage.com/readme.md",
            "https://path-to-storage.com/shapefile.shp",
            "https://deafrica-sentinel-1.s3.af-south-1.amazonaws.com/s1_rtc/N13E025/2018/01/04/0101B0/s1_rtc_0101B0_N13E025_2018_01_04_ANGLE.tif"
        ]
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        example={
            "ID": "example_stac_item"
        }
    )
    metadata_url: Optional[str] = Field(
        None,
        example="https://path-to-storage.com/SX8888.json"
    )
    parser: Optional[str] = Field(
        None,
        example="example"
    )

    @root_validator
    def fetch_metadata(cls, values):
        metadata = values.get("metadata")
        metadata_url = values.get("metadata_url")

        # Check if there isn't a metadata provided but there is a metadata_url
        if not metadata and metadata_url:
            try:
                # Fetch the content from the metadata URL
                response = requests.get(metadata_url)
                response.raise_for_status()
                values["metadata"] = response.json()
            except Exception as e:
                raise ValueError(f"Failed to fetch metadata from {metadata_url}: {e}")

        return values
