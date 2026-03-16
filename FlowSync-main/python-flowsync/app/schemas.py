"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field


# ─── Node Types ──────────────────────────────────────────────────────────────

NodeType = Literal["start", "end", "action", "condition", "delay", "fork", "join", "transform", "webhook_response"]


class WorkflowNode(BaseModel):
    """Workflow node definition."""
    id: str
    type: NodeType
    label: str
    config: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Dict[str, float]] = None  # {x: float, y: float}


class WorkflowEdge(BaseModel):
    """Workflow edge definition."""
    id: str
    source: str
    target: str
    condition: Optional[str] = None
    condition_branch: Optional[Literal["true", "false"]] = Field(None, alias="conditionBranch")
    
    class Config:
        populate_by_name = True


class WorkflowDefinition(BaseModel):
    """Complete workflow definition (DAG)."""
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]


# ─── Workflow Schemas ────────────────────────────────────────────────────────

WorkflowStatus = Literal["draft", "active", "archived"]


class WorkflowCreate(BaseModel):
    """Schema for creating a workflow."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    definition_json: WorkflowDefinition = Field(..., alias="definitionJson")
    
    class Config:
        populate_by_name = True


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    definition_json: Optional[WorkflowDefinition] = Field(None, alias="definitionJson")
    status: Optional[WorkflowStatus] = None
    
    class Config:
        populate_by_name = True


class WorkflowResponse(BaseModel):
    """Schema for workflow response."""
    id: str
    name: str
    description: Optional[str]
    version: int
    definition_json: Dict[str, Any] = Field(..., alias="definitionJson")
    status: str
    user_id: Optional[str] = Field(None, alias="userId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True


# ─── Execution Schemas ───────────────────────────────────────────────────────

ExecutionStatus = Literal["pending", "running", "completed", "failed", "cancelled"]


class ExecutionCreate(BaseModel):
    """Schema for starting an execution."""
    workflow_id: str = Field(..., alias="workflowId")
    input: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True


class ExecutionResponse(BaseModel):
    """Schema for execution response."""
    id: str
    workflow_id: str = Field(..., alias="workflowId")
    status: str
    input: Optional[Dict[str, Any]]
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    user_id: Optional[str] = Field(None, alias="userId")
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    created_at: datetime = Field(..., alias="createdAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True


# ─── Trigger Schemas ─────────────────────────────────────────────────────────

TriggerType = Literal["manual", "webhook", "cron"]


class TriggerCreate(BaseModel):
    """Schema for creating a trigger."""
    workflow_id: str = Field(..., alias="workflowId")
    type: TriggerType
    config: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True


class TriggerUpdate(BaseModel):
    """Schema for updating a trigger."""
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class TriggerResponse(BaseModel):
    """Schema for trigger response."""
    id: str
    workflow_id: str = Field(..., alias="workflowId")
    type: str
    enabled: bool
    config: Optional[Dict[str, Any]]
    last_fired_at: Optional[datetime] = Field(None, alias="lastFiredAt")
    next_run_at: Optional[datetime] = Field(None, alias="nextRunAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True


# ─── API Response Schemas ────────────────────────────────────────────────────

class ApiResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    errors: Optional[List[str]] = None


class ValidationResult(BaseModel):
    """DAG validation result."""
    valid: bool
    errors: List[str] = Field(default_factory=list)

