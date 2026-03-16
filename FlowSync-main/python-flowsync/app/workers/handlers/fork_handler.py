"""Fork node handler."""

import time
from app.workers.worker_types import WorkerJob, WorkerResult


class ForkHandler:
    """Handles 'fork' nodes - splits execution into parallel branches."""
    
    type = "fork"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute fork node - passes through data for parallel execution."""
        start = time.time()
        
        # Fork node just passes through the previous results
        # The orchestrator handles spawning parallel branches
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

