"""Handler registry for mapping node types to action handlers."""

from typing import Dict, Optional, Protocol
from app.workers.worker_types import WorkerJob, WorkerResult


class ActionHandler(Protocol):
    """Protocol for action handlers."""
    type: str
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        """Execute the job and return a result."""
        ...


class HandlerRegistry:
    """Registry for action handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, ActionHandler] = {}
    
    def register(self, handler: ActionHandler):
        """Register an action handler for a given node type."""
        self._handlers[handler.type] = handler
    
    def get(self, node_type: str) -> Optional[ActionHandler]:
        """Look up the handler for a node type."""
        return self._handlers.get(node_type)
    
    def has(self, node_type: str) -> bool:
        """Check if a handler exists for the given type."""
        return node_type in self._handlers
    
    def list_types(self) -> list[str]:
        """List all registered handler types."""
        return list(self._handlers.keys())


# Global registry instance
registry = HandlerRegistry()

