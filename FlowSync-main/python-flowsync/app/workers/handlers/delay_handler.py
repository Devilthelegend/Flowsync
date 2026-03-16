"""Delay node handler."""

import time
import asyncio
from app.workers.worker_types import WorkerJob, WorkerResult


class DelayHandler:
    """Handles 'delay' nodes - introduces a delay in workflow execution."""
    
    type = "delay"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute delay node."""
        start = time.time()
        node = job.node
        
        # Get delay duration from config (in milliseconds)
        delay_ms = node.config.get("delayMs", 1000)
        
        # Sleep for the specified duration
        await asyncio.sleep(delay_ms / 1000.0)
        
        duration_ms = int((time.time() - start) * 1000)
        
        return WorkerResult(
            job_id=job.id,
            step_id=job.step_id,
            execution_id=job.execution_id,
            status="completed",
            result={"delayed_ms": delay_ms},
            duration_ms=duration_ms,
        )

