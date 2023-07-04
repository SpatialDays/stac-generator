from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from loguru import logger

from app.stac import router as stac_router
from app.core.main_router import router as main_router
from app.core.logger import init_logging

from app.stac.services.metadata_parsers.metadata_parser_manager import (
    MetadataParserManager,
)

load_dotenv(".env")

root_router = APIRouter()

app = FastAPI(title="STAC Generator API", version="0.1.0")


@app.on_event("startup")
def startup_event():
    MetadataParserManager.list_available_parsers()


app.include_router(main_router, tags=["Main"])
app.include_router(stac_router, tags=["STAC"])
app.include_router(root_router, tags=["Root"])

init_logging()

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
