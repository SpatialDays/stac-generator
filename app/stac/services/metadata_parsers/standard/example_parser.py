from loguru import logger


class Parser:
    def parse(self, metadata):
        # Create an empty STAC item to be populated
        stac_item = {"type": "Feature", "stac_extensions": [], "properties": {}}

        # Extract necessary information from the metadata
        stac_item["id"] = metadata["ID"]

        # Return the item to be merged with the main STAC item
        return stac_item
