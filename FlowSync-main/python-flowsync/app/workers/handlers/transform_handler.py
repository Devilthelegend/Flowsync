"""Transform node handler."""

import time
import json
from typing import Any, Dict
from app.workers.worker_types import WorkerJob, WorkerResult


class TransformHandler:
    """Handles 'transform' nodes - transforms data using JSONPath or custom logic."""
    
    type = "transform"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute transform node."""
        start = time.time()
        node = job.node
        
        try:
            # Get transform configuration
            transform_type = node.config.get("transformType", "passthrough")
            
            if transform_type == "passthrough":
                result = job.previous_results
            elif transform_type == "jsonpath":
                # Simple JSONPath-like extraction
                path = node.config.get("path", "$")
                result = self._extract_path(job.previous_results, path)
            elif transform_type == "custom":
                # Custom transformation logic
                script = node.config.get("script", "")
                result = self._execute_custom(script, job.previous_results)
            else:
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
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return WorkerResult(
                job_id=job.id,
                step_id=job.step_id,
                execution_id=job.execution_id,
                status="failed",
                error=f"Transform failed: {str(e)}",
                duration_ms=duration_ms,
                retryable=False,
            )
    
    def _extract_path(self, data: Any, path: str) -> Any:
        """Simple path extraction (simplified JSONPath)."""
        if path == "$":
            return data
        
        # Remove leading $. if present
        if path.startswith("$."):
            path = path[2:]
        
        # Split path and traverse
        parts = path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        
        return current
    
    def _execute_custom(self, script: str, data: Any) -> Any:
        """
        Execute custom transformation script.
        WARNING: This is unsafe. In production, use a sandboxed environment.
        """
        # For demo purposes only - DO NOT use in production
        try:
            # Provide data as 'input' variable
            context = {"input": data, "json": json}
            exec(script, {"__builtins__": {}}, context)
            return context.get("output", data)
        except Exception as e:
            raise ValueError(f"Custom script execution failed: {str(e)}")

