"""Trigger API routes."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Trigger
from app.schemas import TriggerCreate, TriggerUpdate, TriggerResponse, ApiResponse

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def list_triggers(
    workflow_id: str = None,
    db: AsyncSession = Depends(get_db),
):
    """List all triggers, optionally filtered by workflow_id."""
    try:
        query = select(Trigger).order_by(Trigger.created_at.desc())
        
        if workflow_id:
            query = query.where(Trigger.workflow_id == workflow_id)
        
        result = await db.execute(query)
        triggers = result.scalars().all()
        
        return ApiResponse(
            success=True,
            data=[TriggerResponse.model_validate(t) for t in triggers]
        )
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@router.post("", response_model=ApiResponse, status_code=201)
async def create_trigger(
    trigger: TriggerCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new trigger."""
    try:
        new_trigger = Trigger(
            workflow_id=trigger.workflow_id,
            type=trigger.type,
            enabled=True,
            config=trigger.config,
        )
        db.add(new_trigger)
        await db.commit()
        await db.refresh(new_trigger)
        
        return ApiResponse(
            success=True,
            data=TriggerResponse.model_validate(new_trigger)
        )
    except Exception as e:
        await db.rollback()
        return ApiResponse(success=False, error=str(e))


@router.get("/{trigger_id}", response_model=ApiResponse)
async def get_trigger(
    trigger_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single trigger by ID."""
    try:
        result = await db.execute(
            select(Trigger).where(Trigger.id == trigger_id)
        )
        trigger = result.scalar_one_or_none()
        
        if not trigger:
            raise HTTPException(status_code=404, detail="Trigger not found")
        
        return ApiResponse(
            success=True,
            data=TriggerResponse.model_validate(trigger)
        )
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@router.put("/{trigger_id}", response_model=ApiResponse)
async def update_trigger(
    trigger_id: str,
    trigger_update: TriggerUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a trigger."""
    try:
        result = await db.execute(
            select(Trigger).where(Trigger.id == trigger_id)
        )
        trigger = result.scalar_one_or_none()
        
        if not trigger:
            raise HTTPException(status_code=404, detail="Trigger not found")
        
        if trigger_update.enabled is not None:
            trigger.enabled = trigger_update.enabled
        if trigger_update.config is not None:
            trigger.config = trigger_update.config
        
        await db.commit()
        await db.refresh(trigger)
        
        return ApiResponse(
            success=True,
            data=TriggerResponse.model_validate(trigger)
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return ApiResponse(success=False, error=str(e))


@router.delete("/{trigger_id}", response_model=ApiResponse)
async def delete_trigger(
    trigger_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a trigger."""
    try:
        result = await db.execute(
            select(Trigger).where(Trigger.id == trigger_id)
        )
        trigger = result.scalar_one_or_none()
        
        if not trigger:
            raise HTTPException(status_code=404, detail="Trigger not found")
        
        await db.delete(trigger)
        await db.commit()
        
        return ApiResponse(success=True, data={"deleted": True})
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return ApiResponse(success=False, error=str(e))

