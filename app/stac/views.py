from fastapi import APIRouter, Depends, HTTPException
from .models import GenerateSTACPayload
from .services.stac_item_creator import STACItemCreator

router = APIRouter()

@router.post("/stac/generate")
async def generate_stac(item: GenerateSTACPayload = Depends()):
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
        return STACItemCreator(item.dict()).create_item()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
