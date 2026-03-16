"""Workflow orchestrator - executes workflows by traversing the DAG."""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Workflow, Execution, StepExecution
from app.schemas import WorkflowDefinition
from app.queue.job_queue import job_queue
from app.workers.worker_types import WorkerJob


async def execute_workflow(
    workflow_id: str,
    input_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute a workflow by ID. Creates an Execution record, publishes the
    first batch of ready nodes to the job queue.
    """
    async with AsyncSessionLocal() as session:
        # 1. Load workflow
        result = await session.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        definition = WorkflowDefinition(**workflow.definition_json)
        
        # 2. Create execution record
        execution = Execution(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            status="running",
            input=input_data,
            user_id=user_id,
            started_at=datetime.utcnow(),
        )
        session.add(execution)
        await session.commit()
        await session.refresh(execution)
        
        print(f"🚀 Execution started: {execution.id} for workflow '{workflow.name}'")
        
        # 3. Find initial ready nodes (nodes with no incoming edges)
        nodes_with_incoming = {edge.target for edge in definition.edges}
        initial_nodes = [
            node for node in definition.nodes
            if node.id not in nodes_with_incoming
        ]
        
        if not initial_nodes:
            # No starting nodes → complete immediately
            execution.status = "completed"
            execution.output = {}
            execution.completed_at = datetime.utcnow()
            await session.commit()
            return {
                "execution_id": execution.id,
                "status": "completed",
                "output": {},
            }
        
        # 4. Create step executions for initial nodes
        for node in initial_nodes:
            step = StepExecution(
                id=str(uuid.uuid4()),
                execution_id=execution.id,
                node_id=node.id,
                node_label=node.label,
                node_type=node.type,
                status="pending",
                input=input_data,
            )
            session.add(step)
        
        await session.commit()
        
        # 5. Publish initial jobs to the queue
        for node in initial_nodes:
            # Find the step we just created
            result = await session.execute(
                select(StepExecution).where(
                    StepExecution.execution_id == execution.id,
                    StepExecution.node_id == node.id,
                )
            )
            step = result.scalar_one()
            
            job = WorkerJob(
                id=str(uuid.uuid4()),
                execution_id=execution.id,
                step_id=step.id,
                node=node,
                input=input_data,
                previous_results={},
                attempt=1,
                max_retries=3,
            )
            await job_queue.enqueue(job)
        
        return {
            "execution_id": execution.id,
            "status": "running",
            "workflow_name": workflow.name,
        }


async def cancel_execution(execution_id: str) -> bool:
    """Cancel a running execution."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Execution).where(Execution.id == execution_id)
        )
        execution = result.scalar_one_or_none()
        
        if not execution:
            return False
        
        if execution.status not in ["pending", "running"]:
            return False
        
        execution.status = "cancelled"
        execution.completed_at = datetime.utcnow()
        execution.error = "Execution cancelled by user"
        
        await session.commit()
        
        print(f"🛑 Execution cancelled: {execution_id}")
        return True


async def get_execution_status(execution_id: str) -> Optional[Dict[str, Any]]:
    """Get the current status of an execution."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Execution).where(Execution.id == execution_id)
        )
        execution = result.scalar_one_or_none()
        
        if not execution:
            return None
        
        # Get step executions
        steps_result = await session.execute(
            select(StepExecution).where(StepExecution.execution_id == execution_id)
        )
        steps = steps_result.scalars().all()
        
        return {
            "id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status,
            "input": execution.input,
            "output": execution.output,
            "error": execution.error,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "steps": [
                {
                    "id": step.id,
                    "node_id": step.node_id,
                    "node_label": step.node_label,
                    "node_type": step.node_type,
                    "status": step.status,
                    "attempts": step.attempts,
                    "error": step.error,
                }
                for step in steps
            ],
        }

