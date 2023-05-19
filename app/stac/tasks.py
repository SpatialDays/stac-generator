from .models import GenerateSTACPayload
from .services.stac_item_creator import STACItemCreator
from loguru import logger


def create_item(item_dict: dict):
    """
    Creates a STAC item based on provided dictionary.
    This function serves as a wrapper for STACItemCreator class to be compatible with RQ jobs.

    Args:
        item_dict (dict): Dictionary containing information necessary to create a STAC item.

    Returns:
        dict: Dictionary with a success message and the created STAC item.
    """
    stac_item_creator = STACItemCreator(item_dict)
    stac_item = stac_item_creator.create_item()

    logger.info(f"Created STAC item: {stac_item}")

    return {
        "message": "STAC Item created",
        "item": stac_item.to_dict(),
    }
