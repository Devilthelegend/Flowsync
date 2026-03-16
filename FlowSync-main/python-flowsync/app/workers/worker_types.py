"""Worker job and result types."""

from typing import Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel

from app.schemas import WorkflowNode


class WorkerJob(BaseModel):
    """Job to be processed by a worker."""
    id: str
    execution_id: str
    step_id: str
    node: WorkflowNode
    input: Optional[Dict[str, Any]] = None
    previous_results: Dict[str, Any] = {}
    attempt: int = 1
    max_retries: int = 3
    created_at: datetime = datetime.utcnow()


class WorkerResult(BaseModel):
    """Result of a worker job execution."""
    job_id: str
    step_id: str
    execution_id: str
    status: Literal["completed", "failed"]
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: int = 0
    retryable: bool = True


class RetryPolicy(BaseModel):
    """Retry policy configuration."""
    backoff_ms: int = 1000
    backoff_multiplier: int = 2
    max_retries: int = 3


# Default retry policy
DEFAULT_RETRY_POLICY = RetryPolicy()

