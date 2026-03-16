"""Queue monitoring API routes."""

from fastapi import APIRouter
from app.schemas import ApiResponse
from app.queue.job_consumer import get_consumer_status

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def get_queue_status():
    """Get queue and consumer status."""
    try:
        status = await get_consumer_status()
        return ApiResponse(success=True, data=status)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

