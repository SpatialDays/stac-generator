from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class GDALInfos(BaseModel):
    tiffUrl: HttpUrl
    gdalInfo: dict


class GenerateSTACPayload(BaseModel):
    gdalInfos: List[GDALInfos]
    files: List[HttpUrl]
    metadata: Optional[List[HttpUrl]]
    method: str = "POST"
