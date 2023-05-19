from loguru import logger
from fastapi import Depends, APIRouter, HTTPException


router = APIRouter()


@router.get("/", status_code=200)
async def status():

    """
    Nothing to see here, move along.

    Returns:
        str: Hello World
    """

    return 'Hello World'
