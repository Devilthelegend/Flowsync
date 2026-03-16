"""PostgreSQL-backed job queue with SELECT FOR UPDATE SKIP LOCKED."""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import JobQueue as JobQueueModel
from app.workers.worker_types import WorkerJob


class JobQueue:
    """PostgreSQL-backed persistent job queue."""
    
    def __init__(self):
        self._total_enqueued = 0
        self._total_processed = 0
        self._total_failed = 0
        self._listeners = []
    
    async def enqueue(self, job: WorkerJob) -> None:
        """Add a job to the persistent queue."""
        async with AsyncSessionLocal() as session:
            try:
                job_record = JobQueueModel(
                    id=job.id,
                    execution_id=job.execution_id,
                    node_id=job.node.id,
                    node_label=job.node.label,
                    node_type=job.node.type,
                    payload=job.model_dump(mode='json'),
                    status="pending",
                    attempts=0,
                    max_attempts=job.max_retries + 1,
                )
                session.add(job_record)
                await session.commit()
                self._total_enqueued += 1
                
                # Notify listeners
                await self._notify_listeners(job)
            except Exception as e:
                await session.rollback()
                print(f"Error enqueueing job: {e}")
                # Still notify listeners for in-memory fallback
                self._total_enqueued += 1
                await self._notify_listeners(job)
    
    async def dequeue(self, worker_id: str) -> Optional[WorkerJob]:
        """
        Dequeue next pending job using row-level locking.
        Returns None if no jobs available.
        """
        async with AsyncSessionLocal() as session:
            try:
                # Use raw SQL for SELECT FOR UPDATE SKIP LOCKED
                result = await session.execute(
                    text("""
                        SELECT id FROM job_queue
                        WHERE status = 'pending'
                        ORDER BY created_at ASC
                        LIMIT 1
                        FOR UPDATE SKIP LOCKED
                    """)
                )
                row = result.fetchone()
                
                if not row:
                    return None
                
                job_id = row[0]
                
                # Update job status
                stmt = (
                    update(JobQueueModel)
                    .where(JobQueueModel.id == job_id)
                    .values(
                        status="processing",
                        locked_at=datetime.utcnow(),
                        locked_by=worker_id,
                        attempts=JobQueueModel.attempts + 1,
                    )
                    .returning(JobQueueModel)
                )
                result = await session.execute(stmt)
                job_row = result.fetchone()
                await session.commit()
                
                if job_row:
                    payload = job_row[0].payload
                    return WorkerJob(**payload)
                
                return None
            except Exception as e:
                await session.rollback()
                print(f"Error dequeuing job: {e}")
                return None
    
    async def mark_done(self, job_id: str, result: Any = None) -> None:
        """Mark a job as completed."""
        async with AsyncSessionLocal() as session:
            try:
                stmt = (
                    update(JobQueueModel)
                    .where(JobQueueModel.id == job_id)
                    .values(
                        status="completed",
                        completed_at=datetime.utcnow(),
                        result=result,
                    )
                )
                await session.execute(stmt)
                await session.commit()
                self._total_processed += 1
            except Exception as e:
                await session.rollback()
                print(f"Error marking job done: {e}")
    
    async def mark_failed(self, job_id: str, error: str) -> None:
        """Mark a job as failed."""
        async with AsyncSessionLocal() as session:
            try:
                stmt = (
                    update(JobQueueModel)
                    .where(JobQueueModel.id == job_id)
                    .values(
                        status="failed",
                        completed_at=datetime.utcnow(),
                        error=error,
                    )
                )
                await session.execute(stmt)
                await session.commit()
                self._total_failed += 1
            except Exception as e:
                await session.rollback()
                print(f"Error marking job failed: {e}")
    
    async def get_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    select(JobQueueModel).where(JobQueueModel.status == "pending")
                )
                depth = len(result.fetchall())
                
                return {
                    "depth": depth,
                    "total_enqueued": self._total_enqueued,
                    "total_processed": self._total_processed,
                    "total_failed": self._total_failed,
                }
            except Exception:
                return {
                    "depth": 0,
                    "total_enqueued": self._total_enqueued,
                    "total_processed": self._total_processed,
                    "total_failed": self._total_failed,
                }
    
    def on_job(self, callback):
        """Register a callback for new jobs."""
        self._listeners.append(callback)
    
    async def _notify_listeners(self, job: WorkerJob):
        """Notify all listeners of a new job."""
        for callback in self._listeners:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(job)
                else:
                    callback(job)
            except Exception as e:
                print(f"Error notifying listener: {e}")


# Global job queue instance
job_queue = JobQueue()

