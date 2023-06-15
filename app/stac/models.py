from typing import List, Optional
from pydantic import BaseModel


class GenerateSTACPayload(BaseModel):
    files: List[str]
    metadata: dict
    metadata_url: Optional[str]
    parser: Optional[str]
