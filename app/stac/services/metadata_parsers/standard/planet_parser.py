import logging
import requests
import json

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self):
        pass

    def parse(self, payload, **kwargs):
        stac_item = {
            "type": "Feature",
            "stac_extensions": [
                "https://stac-extensions.github.io/view/v1.0.0/schema.json"
            ],
            "properties": {},
        }

        # Find the metadata file and parse its JSON, the file is called _metadata.JSON
        metadata_file = next(
            (file for file in payload.files if "_metadata.json" in file), None
        )
        if not metadata_file:
            logger.error("Metadata file not found in the provided payload.")
            return stac_item

        logger.info(f"Found metadata file {metadata_file} in the provided payload.")
        res = requests.get(metadata_file)
        metadata = json.loads(res.text)

        elements_to_extract = {
            "view_angle": {"name": "view:off_nadir", "parser": float},
            "cloud_cover": {"name": "eo:cloud_cover", "parser": float},
            "gsd": {"name": "gsd", "parser": float},
            "satellite_azimuth": {"name": "view:azimuth", "parser": float},
            "sun_azimuth": {"name": "view:sun_azimuth", "parser": float},
        }

        for json_key, props in elements_to_extract.items():
            value = metadata['properties'].get(json_key)  # Returns None if the key doesn't exist
            if value is not None:
                stac_item["properties"][props["name"]] = props["parser"](value)
            else:
                logger.error(f"{json_key} key not found within metadata.")

        return stac_item
