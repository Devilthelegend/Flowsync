"""Cron-based scheduler for workflow triggers."""

import asyncio
from datetime import datetime
from typing import Optional
from croniter import croniter
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Trigger
from app.orchestrator import execute_workflow
from app.config import settings


class Scheduler:
    """Cron-based scheduler for workflow triggers."""
    
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._triggers_fired = 0
        self._errors = 0
    
    def start(self):
        """Start the scheduler."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        print(f"✅ Scheduler started (interval: {settings.scheduler_interval_seconds}s)")
    
    def stop(self):
        """Stop the scheduler."""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
        print("✅ Scheduler stopped")
    
    async def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            try:
                await self._check_triggers()
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                self._errors += 1
            
            await asyncio.sleep(settings.scheduler_interval_seconds)
    
    async def _check_triggers(self):
        """Check for cron triggers that need to fire."""
        async with AsyncSessionLocal() as session:
            # Find enabled cron triggers
            result = await session.execute(
                select(Trigger).where(
                    Trigger.type == "cron",
                    Trigger.enabled == True,
                )
            )
            triggers = result.scalars().all()
            
            now = datetime.utcnow()
            
            for trigger in triggers:
                try:
                    config = trigger.config or {}
                    expression = config.get("expression")
                    
                    if not expression:
                        continue
                    
                    # Check if trigger should fire
                    should_fire = False
                    
                    if trigger.next_run_at:
                        # Check if next_run_at has passed
                        should_fire = trigger.next_run_at <= now
                    else:
                        # First time - calculate next run
                        should_fire = True
                    
                    if should_fire:
                        print(f"🔔 Firing cron trigger {trigger.id} (expression: {expression})")
                        
                        # Get trigger input
                        trigger_input = config.get("input", {})
                        
                        # Calculate next run time
                        next_run = self._get_next_run_time(expression)
                        
                        # Update trigger
                        trigger.last_fired_at = now
                        if next_run:
                            trigger.next_run_at = next_run
                        await session.commit()
                        
                        # Execute workflow (fire-and-forget)
                        asyncio.create_task(
                            self._execute_workflow_safe(trigger.workflow_id, trigger_input)
                        )
                        
                        self._triggers_fired += 1
                
                except Exception as e:
                    print(f"❌ Error processing trigger {trigger.id}: {e}")
                    self._errors += 1
    
    async def _execute_workflow_safe(self, workflow_id: str, input_data: dict):
        """Execute workflow with error handling."""
        try:
            await execute_workflow(workflow_id, input_data)
        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
            self._errors += 1
    
    def _get_next_run_time(self, expression: str) -> Optional[datetime]:
        """Calculate next run time from cron expression."""
        try:
            cron = croniter(expression, datetime.utcnow())
            return cron.get_next(datetime)
        except Exception as e:
            print(f"❌ Invalid cron expression '{expression}': {e}")
            return None
    
    def get_status(self) -> dict:
        """Get scheduler status."""
        return {
            "running": self._running,
            "triggers_fired": self._triggers_fired,
            "errors": self._errors,
        }


# Global scheduler instance
scheduler = Scheduler()

