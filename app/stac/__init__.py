from fastapi import APIRouter
from app.stac.views import router

API_STR = "/stac"

stac_router = APIRouter(prefix=API_STR)
stac_router.include_router(router)
