"""Condition node handler."""

import time
from app.workers.worker_types import WorkerJob, WorkerResult


class ConditionHandler:
    """Handles 'condition' nodes - evaluates conditions for branching."""
    
    type = "condition"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute condition node."""
        start = time.time()
        node = job.node
        
        # Get condition expression from config
        condition_expr = node.config.get("condition", "true")
        
        # Simple evaluation - in production, use a safe expression evaluator
        try:
            # For now, support simple boolean expressions
            result = self._evaluate_condition(condition_expr, job.previous_results)
            
            duration_ms = int((time.time() - start) * 1000)
            
            return WorkerResult(
                job_id=job.id,
                step_id=job.step_id,
                execution_id=job.execution_id,
                status="completed",
                result={"condition_result": result},
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return WorkerResult(
                job_id=job.id,
                step_id=job.step_id,
                execution_id=job.execution_id,
                status="failed",
                error=f"Condition evaluation failed: {str(e)}",
                duration_ms=duration_ms,
                retryable=False,
            )
    
    def _evaluate_condition(self, expr: str, context: dict) -> bool:
        """
        Evaluate a condition expression.
        WARNING: This is a simplified implementation. In production, use a safe
        expression evaluator like simpleeval or implement a proper DSL.
        """
        # For demo purposes, support simple comparisons
        if expr.lower() in ["true", "1"]:
            return True
        if expr.lower() in ["false", "0"]:
            return False
        
        # Try to evaluate with context (UNSAFE - for demo only)
        try:
            # In production, use a safe evaluator
            return bool(eval(expr, {"__builtins__": {}}, context))
        except Exception:
            return False

