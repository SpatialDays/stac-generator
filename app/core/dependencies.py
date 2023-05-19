from typing import Dict
from fastapi import Depends, FastAPI
from starlette.requests import Request

def get_redis_queue(request: Request):
    return request.app.state.redis_queue
