"""Health check API routes."""

import time
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ApiResponse
from app.queue.job_consumer import get_consumer_status

router = APIRouter()

start_time = time.time()


@router.get("", response_model=ApiResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check / readiness probe."""
    try:
        # 1. DB connectivity check
        db_status = "healthy"
        db_latency_ms = 0
        try:
            db_start = time.time()
            await db.execute(text("SELECT 1"))
            db_latency_ms = int((time.time() - db_start) * 1000)
        except Exception:
            db_status = "unhealthy"
        
        # 2. Consumer status
        consumer = await get_consumer_status()
        
        # 3. Uptime
        uptime_seconds = int(time.time() - start_time)
        
        is_healthy = db_status == "healthy" and consumer["is_running"]
        
        health_data = {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime_seconds,
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms,
            },
            "consumer": {
                "is_running": consumer["is_running"],
                "worker_id": consumer["worker_id"],
                "active_jobs": consumer["active_jobs"],
                "max_concurrency": consumer["max_concurrency"],
            },
            "queue": consumer["queue_stats"],
        }
        
        return ApiResponse(success=True, data=health_data)
    except Exception as e:
        return ApiResponse(
            success=False,
            error=str(e),
            data={"status": "unhealthy"}
        )

