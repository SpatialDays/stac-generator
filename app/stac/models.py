from typing import List, Optional
from pydantic import BaseModel


class GenerateSTACPayload(BaseModel):
    files: List[str]
    metadata: Optional[dict]
    method: Optional[str] = "POST"
    parser: Optional[str]
