"""Execution API routes."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Execution
from app.schemas import ExecutionCreate, ExecutionResponse, ApiResponse
from app.orchestrator import execute_workflow, cancel_execution, get_execution_status

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def list_executions(
    workflow_id: str = None,
    db: AsyncSession = Depends(get_db),
):
    """List all executions, optionally filtered by workflow_id."""
    try:
        query = select(Execution).order_by(Execution.created_at.desc())
        
        if workflow_id:
            query = query.where(Execution.workflow_id == workflow_id)
        
        result = await db.execute(query)
        executions = result.scalars().all()
        
        return ApiResponse(
            success=True,
            data=[ExecutionResponse.model_validate(e) for e in executions]
        )
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@router.post("", response_model=ApiResponse, status_code=201)
async def start_execution(
    execution: ExecutionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Start a new workflow execution."""
    try:
        result = await execute_workflow(
            workflow_id=execution.workflow_id,
            input_data=execution.input,
            # user_id=user_id,  # TODO: Add auth
        )
        
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@router.get("/{execution_id}", response_model=ApiResponse)
async def get_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get execution details including steps."""
    try:
        status = await get_execution_status(execution_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return ApiResponse(success=True, data=status)
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@router.post("/{execution_id}/cancel", response_model=ApiResponse)
async def cancel_execution_route(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running execution."""
    try:
        success = await cancel_execution(execution_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Execution not found or cannot be cancelled"
            )
        
        return ApiResponse(success=True, data={"cancelled": True})
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

