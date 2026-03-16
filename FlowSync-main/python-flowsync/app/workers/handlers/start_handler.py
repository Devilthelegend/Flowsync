"""Start node handler."""

import time
from app.workers.worker_types import WorkerJob, WorkerResult


class StartHandler:
    """Handles 'start' nodes - entry point of workflow."""
    
    type = "start"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute start node - simply passes through input."""
        start = time.time()
        
        # Start node just passes through the input
        result = job.input or {}
        
        duration_ms = int((time.time() - start) * 1000)
        
        return WorkerResult(
            job_id=job.id,
            step_id=job.step_id,
            execution_id=job.execution_id,
            status="completed",
            result=result,
            duration_ms=duration_ms,
        )

