"""Job consumer - worker loop that processes jobs from the queue."""

import asyncio
import uuid
from datetime import datetime
from typing import Optional

from app.queue.job_queue import job_queue
from app.workers.handler_registry import registry
from app.workers.worker_types import WorkerJob, WorkerResult, DEFAULT_RETRY_POLICY
from app.database import AsyncSessionLocal
from app.models import StepExecution
from app.config import settings
from sqlalchemy import select, update


# Consumer state
is_running = False
is_shutting_down = False
active_jobs = 0
total_retries = 0
MAX_CONCURRENCY = settings.max_worker_concurrency
POLL_INTERVAL_MS = settings.worker_poll_interval_ms
poll_task: Optional[asyncio.Task] = None

# Unique worker ID
WORKER_ID = f"worker-{str(uuid.uuid4())[:8]}"


def start_consumer():
    """Start the consumer loop."""
    global is_running, poll_task
    
    if is_running:
        return
    
    is_running = True
    print(f"✅ Consumer started: {WORKER_ID}, poll interval: {POLL_INTERVAL_MS}ms")
    
    # Listen for event-driven notifications
    job_queue.on_job(lambda job: asyncio.create_task(drain_queue()))
    
    # Start polling task
    poll_task = asyncio.create_task(poll_loop())


async def poll_loop():
    """Poll the database for pending jobs."""
    while is_running and not is_shutting_down:
        await drain_queue()
        await asyncio.sleep(POLL_INTERVAL_MS / 1000.0)


async def drain_queue():
    """Process jobs from the queue up to the concurrency limit."""
    global active_jobs
    
    if is_shutting_down:
        return
    
    while active_jobs < MAX_CONCURRENCY:
        active_jobs += 1
        
        # Launch async job processing
        asyncio.create_task(process_next_job())
        break  # Only launch one at a time per drain call


async def process_next_job():
    """Dequeue and process the next job."""
    global active_jobs
    
    try:
        job = await job_queue.dequeue(WORKER_ID)
        if not job:
            active_jobs -= 1
            return
        
        try:
            await process_job(job)
        finally:
            active_jobs -= 1
            # Try to drain more after completing
            await drain_queue()
    except Exception as e:
        print(f"Error in process_next_job: {e}")
        active_jobs -= 1


async def process_job(job: WorkerJob):
    """Process a single job through its action handler."""
    
    # Mark step as running
    async with AsyncSessionLocal() as session:
        try:
            stmt = (
                update(StepExecution)
                .where(StepExecution.id == job.step_id)
                .values(
                    status="running",
                    started_at=datetime.utcnow(),
                    attempts=job.attempt,
                )
            )
            await session.execute(stmt)
            await session.commit()
        except Exception:
            await session.rollback()
            await job_queue.mark_failed(job.id, "Step no longer exists or was cancelled")
            return
    
    # Find the handler
    handler = registry.get(job.node.type)
    
    if not handler:
        result = WorkerResult(
            job_id=job.id,
            step_id=job.step_id,
            execution_id=job.execution_id,
            status="failed",
            error=f'No handler registered for node type: "{job.node.type}"',
            duration_ms=0,
            retryable=False,
        )
        await job_queue.mark_failed(job.id, result.error)
    else:
        try:
            result = await handler.execute(job)
            
            if result.status == "completed":
                await job_queue.mark_done(job.id, result.result)
            else:
                await job_queue.mark_failed(job.id, result.error)
        except Exception as e:
            result = WorkerResult(
                job_id=job.id,
                step_id=job.step_id,
                execution_id=job.execution_id,
                status="failed",
                error=str(e),
                duration_ms=0,
                retryable=True,
            )
            await job_queue.mark_failed(job.id, result.error)
    
    # ─── Retry Logic ─────────────────────────────────────────────────────
    if (
        result.status == "failed"
        and result.retryable
        and job.attempt < job.max_retries
    ):
        retry_config = get_retry_config(job.node.config)
        delay = retry_config.backoff_ms * (retry_config.backoff_multiplier ** (job.attempt - 1))
        
        print(f"⚠️  Retrying job {job.id} (attempt {job.attempt}/{job.max_retries}) after {delay}ms")
        
        global total_retries
        total_retries += 1
        
        # Update step to show retry pending
        async with AsyncSessionLocal() as session:
            stmt = (
                update(StepExecution)
                .where(StepExecution.id == job.step_id)
                .values(
                    status="pending",
                    error=f"Retry {job.attempt}/{job.max_retries}: {result.error}",
                    attempts=job.attempt,
                )
            )
            await session.execute(stmt)
            await session.commit()
        
        # Re-enqueue after backoff delay
        await asyncio.sleep(delay / 1000.0)
        retry_job = job.model_copy(update={"attempt": job.attempt + 1, "created_at": datetime.utcnow()})
        await job_queue.enqueue(retry_job)
        return
    
    # If permanently failed, log it
    if result.status == "failed" and job.max_retries > 0:
        print(f"❌ Job {job.id} moved to DLQ after {job.attempt} attempts")
    
    # Feed result to result handler (to be implemented)
    # await handle_result(result)


def get_retry_config(config: dict):
    """Extract retry config from node config."""
    retry = config.get("retry", {})
    return DEFAULT_RETRY_POLICY.model_copy(
        update={
            "backoff_ms": retry.get("backoffMs", DEFAULT_RETRY_POLICY.backoff_ms),
            "backoff_multiplier": retry.get("backoffMultiplier", DEFAULT_RETRY_POLICY.backoff_multiplier),
        }
    )


async def get_consumer_status():
    """Get consumer status info."""
    return {
        "is_running": is_running,
        "worker_id": WORKER_ID,
        "active_jobs": active_jobs,
        "max_concurrency": MAX_CONCURRENCY,
        "total_retries": total_retries,
        "queue_stats": await job_queue.get_stats(),
    }


async def stop_consumer():
    """Graceful shutdown: stop accepting new jobs and wait for active ones."""
    global is_running, is_shutting_down, poll_task
    
    if not is_running:
        return
    
    is_shutting_down = True
    
    # Cancel polling task
    if poll_task:
        poll_task.cancel()
        try:
            await poll_task
        except asyncio.CancelledError:
            pass
    
    print(f"🛑 Consumer shutting down, waiting for {active_jobs} active jobs...")
    
    # Wait for active jobs to finish (max 30s)
    max_wait = 30
    waited = 0
    while active_jobs > 0 and waited < max_wait:
        await asyncio.sleep(0.5)
        waited += 0.5
    
    is_running = False
    is_shutting_down = False
    print(f"✅ Consumer stopped (active jobs remaining: {active_jobs})")

