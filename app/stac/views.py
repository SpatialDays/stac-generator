from loguru import logger
from fastapi import Depends, APIRouter
from .models import GenerateSTACPayload

router = APIRouter()


@router.post("/stac/generate")
async def generate_stac(item: GenerateSTACPayload):
    return {"message": "STAC generation started"}
