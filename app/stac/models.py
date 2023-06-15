from typing import List, Optional, Dict, Any
from pydantic import BaseModel, root_validator
from loguru import logger
import requests


class GenerateSTACPayload(BaseModel):
    files: List[str]
    metadata: Optional[Dict[str, Any]]
    metadata_url: Optional[str]
    parser: Optional[str]

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

        # At least one of metadata or metadata_url should be provided
        if not metadata and not metadata_url:
            raise ValueError(
                "At least one of metadata or metadata_url should be provided"
            )

        return values
