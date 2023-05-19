from .models import GenerateSTACPayload
import logging


def create_item(item_dict: dict):
    item = GenerateSTACPayload(**item_dict)
    logging.info(f"Created item: {item}")
    return True
