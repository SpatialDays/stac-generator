from fastapi import Depends
from rq import Queue
from fastapi import APIRouter
from .models import GenerateSTACPayload
from app.core.dependencies import get_redis_queue

router = APIRouter()

@router.post("/stac/generate")
async def generate_stac(item: GenerateSTACPayload, queue: Queue = Depends(get_redis_queue)):
    # Create a new job and add it to the queue
    job = queue.enqueue("stac_generator.create_item", item.dict())
    return {"message": "STAC generation started", "job_id": job.get_id()}
