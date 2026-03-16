"""Action node handler - supports HTTP requests and simulated actions."""

import time
import asyncio
import httpx
from typing import Any, Dict
from app.workers.worker_types import WorkerJob, WorkerResult


class ActionNodeHandler:
    """Handles 'action' nodes - HTTP requests or simulated actions."""
    
    type = "action"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute action node."""
        start = time.time()
        node = job.node
        action_type = node.config.get("actionType", "default")
        
        try:
            if action_type == "http":
                result = await self._execute_http(node.config)
            else:
                result = await self._execute_simulated(node.config)
            
            duration_ms = int((time.time() - start) * 1000)
            
            return WorkerResult(
                job_id=job.id,
                step_id=job.step_id,
                execution_id=job.execution_id,
                status="completed",
                result=result,
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return WorkerResult(
                job_id=job.id,
                step_id=job.step_id,
                execution_id=job.execution_id,
                status="failed",
                error=str(e),
                duration_ms=duration_ms,
                retryable=True,
            )
    
    async def _execute_http(self, config: Dict[str, Any]) -> Any:
        """Execute HTTP request."""
        url = config.get("url", "")
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = config.get("body")
        timeout = config.get("timeout", 30)
        
        if not url:
            raise ValueError("HTTP action requires 'url' in config")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=body)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=body)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            try:
                return response.json()
            except Exception:
                return {"status": response.status_code, "text": response.text}
    
    async def _execute_simulated(self, config: Dict[str, Any]) -> Any:
        """Execute simulated action with delay."""
        delay_ms = config.get("delayMs", 100)
        await asyncio.sleep(delay_ms / 1000.0)
        
        return {
            "simulated": True,
            "delay_ms": delay_ms,
            "message": "Simulated action completed",
        }

