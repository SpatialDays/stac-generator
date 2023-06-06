from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class GenerateSTACPayload(BaseModel):
    files: List[str]
    metadata: Optional[List[HttpUrl]]
    method: Optional[str] = "POST"
