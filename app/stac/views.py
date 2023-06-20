from os import getenv
from loguru import logger

from fastapi import APIRouter, HTTPException
from .models import GenerateSTACPayload
from .services.stac_item_creator import STACItemCreator
from .services.publisher.publisher_utility import publish_to_stac_fastapi

import json

router = APIRouter()


@router.post("/stac/generate")
async def generate_stac(item: GenerateSTACPayload):
    """
    Generate a STAC (SpatioTemporal Asset Catalog) item from the provided payload.

    This endpoint receives a POST request containing data for a STAC item generation.
    The payload (item) is passed to the STACItemCreator service which handles the creation
    of the STAC item.

    Args:
        item (GenerateSTACPayload): The payload received from the POST request.

    Returns:
        GenerateSTACPayload: The created STAC item.

    Raises:
        HTTPException: If the STAC item creation fails.
    """
    try:
        stac = STACItemCreator(item.dict()).create_item()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    collection = item.collection or item.parser or "default"
    
    if getenv("HTTP_PUBLISH_TO_STAC_API").lower() == "true":
        try:
            return publish_to_stac_fastapi(stac, collection)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return stac
