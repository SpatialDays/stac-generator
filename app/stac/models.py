from typing import List, Optional
from pydantic import BaseModel

class GenerateSTACPayload(BaseModel):
    source: str
    provider: str
    collection: str
    itemId: Optional[str] = None
    assetPaths: List[str]
    metadataPaths: List[str]
