import logging
import xml.etree.ElementTree as ET
import requests

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

        # Find the metadata file and parse its XML, the file is called DeliveryMetadata.xml
        metadata_file = next(
            (file for file in payload.files if "DeliveryMetadata.xml" in file), None
        )
        if not metadata_file:
            logger.error("Metadata file not found in the provided payload.")
            return stac_item  # or you can handle the error differently

        res = requests.get(metadata_file)
        metadata = ET.fromstring(res.content)

        namespace = {"ns0": "http://xsd.digitalglobe.com/xsd/dm"}
        product_element = metadata.find("ns0:product", namespace)

        if product_element is None:
            logger.error("Product element not found.")
            return stac_item  # or you can handle the error differently

        # Define the XML elements to extract and their desired names in the output
        elements_to_extract = {
            "cloudCover": {
                "name": "eo:cloud_cover",
                "parser": float
            },
            "earliestAcquisitionTime": {
                "name": "datetime",
                "parser": str 
            },
            "sunElevation": {
                "name": "view:sun_elevation",
                "parser": float
            },
            "sunAzimuth": {
                "name": "view:sun_azimuth",
                "parser": float
            }
        }

        for xml_name, props in elements_to_extract.items():
            element = product_element.find(f"ns0:{xml_name}", namespace)
            if element is not None:
                stac_item["properties"][props["name"]] = props["parser"](element.text)
            else:
                logger.error(f"{xml_name} element not found within product.")


        return stac_item
