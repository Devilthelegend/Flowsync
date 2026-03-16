"""End node handler."""

import time
from app.workers.worker_types import WorkerJob, WorkerResult


class EndHandler:
    """Handles 'end' nodes - terminal node of workflow."""
    
    type = "end"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute end node - collects final output."""
        start = time.time()
        
        # End node collects all previous results
        result = job.previous_results
        
        duration_ms = int((time.time() - start) * 1000)
        
        return WorkerResult(
            job_id=job.id,
            step_id=job.step_id,
            execution_id=job.execution_id,
            status="completed",
            result=result,
            duration_ms=duration_ms,
        )

