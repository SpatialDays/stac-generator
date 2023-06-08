from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class GenerateSTACPayload(BaseModel):
    files: List[str]
    metadata: Optional[dict]
    method: Optional[str] = "POST"
    parser: Optional[str] = "example"
