from .models import GenerateSTACPayload
from loguru import logger


def create_item(item_dict: dict):
    item = GenerateSTACPayload(**item_dict)
    return {
        "message": "STAC Item created",
    }
