from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from os import getenv
import threading
from loguru import logger

from app.stac import router as stac_router
from app.core.main_router import router as main_router
from app.core.redis import create_redis_connection, redis_listener
from app.core.logger import init_logging

from app.stac.services.metadata_parsers.metadata_parser_manager import (
    MetadataParserManager,
)

load_dotenv(".env")

root_router = APIRouter()

app = FastAPI(title="STAC Generator API", version="0.1.0")


@app.on_event("startup")
def startup_event():
    try:
        app.state.redis_conn = create_redis_connection()
        app.state.redis_conn.ping()

        app.state.redis_queue_key = getenv("REDIS_INPUT_LIST_NAME")

        if app.state.redis_conn:
            logger.info("Connected to Redis")
            threading.Thread(
                target=redis_listener, args=(app.state.redis_conn, app), daemon=True
            ).start()
        else:
            logger.warning(
                "Could not establish Redis connection, running without Redis."
            )
    except Exception as e:
        logger.error(
            f"Exception occurred while trying to establish Redis connection: {e}"
        )
        logger.warning("Running without Redis.")

    MetadataParserManager.list_available_parsers()


app.include_router(main_router, tags=["Main"])
app.include_router(stac_router, tags=["STAC"])
app.include_router(root_router, tags=["Root"])

init_logging()

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
