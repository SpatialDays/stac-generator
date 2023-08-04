import json
import logging

logging = logging.getLogger(__name__)

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
from blob_mounting_helper_utility import BlobMappingUtility

_blob_mounting_configurations_json_path = os.getenv("BLOB_MOUNTING_CONFIGURATIONS_JSON_PATH",
                                                    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 'blob_mounting_configurations.json'))

_AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", None)

with open(_blob_mounting_configurations_json_path) as json_file:
    blob_mounting_configurations_list: List[Dict[str, Any]] = json.load(json_file)["blob_mounting_configurations"]
blob_mapping_utility: BlobMappingUtility = BlobMappingUtility(blob_mounting_configurations_list,
                                                              _AZURE_STORAGE_ACCOUNT_KEY)

logging.info(f"Using {_blob_mounting_configurations_json_path} for blob mounting configurations")