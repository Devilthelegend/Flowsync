"""Join node handler."""

import time
from app.workers.worker_types import WorkerJob, WorkerResult


class JoinHandler:
    """Handles 'join' nodes - waits for all parallel branches to complete."""
    
    type = "join"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute join node - merges results from parallel branches."""
        start = time.time()
        
        # Join node collects all previous results
        # The orchestrator ensures all incoming branches are complete before executing
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

