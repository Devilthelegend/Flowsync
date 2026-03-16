"""Webhook response node handler."""

import time
from app.workers.worker_types import WorkerJob, WorkerResult


class WebhookResponseHandler:
    """Handles 'webhook_response' nodes - prepares response for webhook triggers."""
    
    type = "webhook_response"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute webhook response node."""
        start = time.time()
        node = job.node
        
        # Get response configuration
        status_code = node.config.get("statusCode", 200)
        response_body = node.config.get("responseBody", job.previous_results)
        
        result = {
            "status_code": status_code,
            "body": response_body,
        }
        
        duration_ms = int((time.time() - start) * 1000)
        
        return WorkerResult(
            job_id=job.id,
            step_id=job.step_id,
            execution_id=job.execution_id,
            status="completed",
            result=result,
            duration_ms=duration_ms,
        )

