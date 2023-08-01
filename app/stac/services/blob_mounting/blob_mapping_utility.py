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
_azure_storage_account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", None)

if not _azure_storage_account_key:
    raise ValueError("AZURE_STORAGE_ACCOUNT_KEY must be defined in the environment")

with open(_blob_mounting_configurations_json_path) as json_file:
    blob_mounting_configurations_list: List[Dict[str, Any]] = json.load(json_file)["blob_mounting_configurations"]
blob_mapping_utility: BlobMappingUtility = BlobMappingUtility(blob_mounting_configurations_list,
                                                              _azure_storage_account_key)

logging.info(f"Using {_blob_mounting_configurations_json_path} for blob mounting configurations")