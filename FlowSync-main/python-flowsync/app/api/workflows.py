"""Workflow API routes."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Workflow
from app.schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse, ApiResponse
from app.dag_validator import validate_dag

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    # user_id: str = Depends(get_current_user)  # TODO: Add auth
):
    """List all workflows for the current user."""
    try:
        result = await db.execute(
            select(Workflow).order_by(Workflow.created_at.desc())
        )
        workflows = result.scalars().all()
        
        return ApiResponse(
            success=True,
            data=[WorkflowResponse.model_validate(w) for w in workflows]
        )
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@router.post("", response_model=ApiResponse, status_code=201)
async def create_workflow(
    workflow: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    # user_id: str = Depends(get_current_user)  # TODO: Add auth
):
    """Create a new workflow."""
    try:
        # Validate DAG structure
        validation = validate_dag(workflow.definition_json)
        if not validation.valid:
            return ApiResponse(
                success=False,
                error="Invalid workflow graph",
                errors=validation.errors,
            )
        
        # Create workflow
        new_workflow = Workflow(
            name=workflow.name,
            description=workflow.description,
            definition_json=workflow.definition_json.model_dump(mode='json'),
            version=1,
            status="draft",
            # user_id=user_id,  # TODO: Add auth
        )
        db.add(new_workflow)
        await db.commit()
        await db.refresh(new_workflow)
        
        return ApiResponse(
            success=True,
            data=WorkflowResponse.model_validate(new_workflow)
        )
    except Exception as e:
        await db.rollback()
        return ApiResponse(success=False, error=str(e))


@router.get("/{workflow_id}", response_model=ApiResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single workflow by ID."""
    try:
        result = await db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return ApiResponse(
            success=True,
            data=WorkflowResponse.model_validate(workflow)
        )
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@router.put("/{workflow_id}", response_model=ApiResponse)
async def update_workflow(
    workflow_id: str,
    workflow_update: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a workflow."""
    try:
        result = await db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Validate DAG if definition is being updated
        if workflow_update.definition_json:
            validation = validate_dag(workflow_update.definition_json)
            if not validation.valid:
                return ApiResponse(
                    success=False,
                    error="Invalid workflow graph",
                    errors=validation.errors,
                )
            workflow.definition_json = workflow_update.definition_json.model_dump(mode='json')
            workflow.version += 1
        
        if workflow_update.name:
            workflow.name = workflow_update.name
        if workflow_update.description is not None:
            workflow.description = workflow_update.description
        if workflow_update.status:
            workflow.status = workflow_update.status
        
        await db.commit()
        await db.refresh(workflow)
        
        return ApiResponse(
            success=True,
            data=WorkflowResponse.model_validate(workflow)
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return ApiResponse(success=False, error=str(e))


@router.delete("/{workflow_id}", response_model=ApiResponse)
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a workflow."""
    try:
        result = await db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        await db.delete(workflow)
        await db.commit()
        
        return ApiResponse(success=True, data={"deleted": True})
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return ApiResponse(success=False, error=str(e))

