"""Webhook API routes."""

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Trigger
from app.schemas import ApiResponse
from app.orchestrator import execute_workflow

router = APIRouter()


@router.post("/{trigger_id}", response_model=ApiResponse)
async def webhook_ingestion(
    trigger_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Webhook ingestion endpoint.
    External systems call this URL to fire a trigger and start a workflow execution.
    """
    try:
        # Load trigger
        result = await db.execute(
            select(Trigger).where(
                Trigger.id == trigger_id,
                Trigger.type == "webhook",
                Trigger.enabled == True,
            )
        )
        trigger = result.scalar_one_or_none()
        
        if not trigger:
            raise HTTPException(
                status_code=404,
                detail="Webhook trigger not found or disabled"
            )
        
        # Get request body
        try:
            body = await request.json()
        except Exception:
            body = {}
        
        # Get trigger input from config
        trigger_input = trigger.config.get("input", {}) if trigger.config else {}
        
        # Merge webhook payload with trigger input
        input_data = {**trigger_input, "webhook_payload": body}
        
        # Execute workflow
        result = await execute_workflow(
            workflow_id=trigger.workflow_id,
            input_data=input_data,
        )
        
        # Update trigger last fired time
        from datetime import datetime
        trigger.last_fired_at = datetime.utcnow()
        await db.commit()
        
        return ApiResponse(
            success=True,
            data={
                "execution_id": result["execution_id"],
                "status": result["status"],
                "message": "Workflow execution started",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

