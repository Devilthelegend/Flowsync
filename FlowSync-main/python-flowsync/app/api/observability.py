"""Observability API routes - metrics and audit logs."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AuditLog
from app.schemas import ApiResponse

router = APIRouter()


@router.get("/metrics", response_model=ApiResponse)
async def get_metrics():
    """Get system metrics."""
    # TODO: Implement metrics collection
    return ApiResponse(
        success=True,
        data={
            "executions_started": 0,
            "executions_completed": 0,
            "executions_failed": 0,
            "jobs_processed": 0,
            "jobs_failed": 0,
        }
    )


@router.get("/audit", response_model=ApiResponse)
async def get_audit_logs(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs."""
    try:
        result = await db.execute(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        
        return ApiResponse(
            success=True,
            data=[
                {
                    "id": log.id,
                    "event": log.event,
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "user_id": log.user_id,
                    "metadata": log.metadata,
                    "created_at": log.created_at.isoformat(),
                }
                for log in logs
            ]
        )
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

