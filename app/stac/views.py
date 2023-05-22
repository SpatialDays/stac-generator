from fastapi import Depends
from fastapi import APIRouter
from .models import GenerateSTACPayload

from .services.stac_item_creator import STACItemCreator

router = APIRouter()


@router.post("/stac/generate")
async def generate_stac(item: GenerateSTACPayload):
    stac = STACItemCreator(item_dict=item.dict()).create_item()
    return {"stac": stac}
