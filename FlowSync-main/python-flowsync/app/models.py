"""SQLAlchemy database models - converted from Prisma schema."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.database import Base


def generate_uuid():
    """Generate UUID string."""
    return str(uuid4())


class Workflow(Base):
    """Workflow model - represents a workflow definition."""
    
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    definition_json = Column(JSON, nullable=False)
    status = Column(String, default="draft", nullable=False)  # draft | active | archived
    user_id = Column(String, nullable=True)  # Clerk user ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    executions = relationship("Execution", back_populates="workflow", cascade="all, delete-orphan")
    triggers = relationship("Trigger", back_populates="workflow", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_workflow_status", "status"),
        Index("idx_workflow_created_at", "created_at"),
        Index("idx_workflow_user_id", "user_id"),
    )


class Execution(Base):
    """Execution model - represents a workflow execution instance."""
    
    __tablename__ = "executions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending | running | completed | failed | cancelled
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    user_id = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    steps = relationship("StepExecution", back_populates="execution", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_execution_workflow_id", "workflow_id"),
        Index("idx_execution_status", "status"),
        Index("idx_execution_created_at", "created_at"),
        Index("idx_execution_user_id", "user_id"),
    )


class StepExecution(Base):
    """StepExecution model - represents execution of a single node."""
    
    __tablename__ = "step_executions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    execution_id = Column(String, ForeignKey("executions.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(String, nullable=False)
    node_label = Column(String, nullable=False)
    node_type = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending | running | completed | failed | skipped
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    execution = relationship("Execution", back_populates="steps")
    
    __table_args__ = (
        Index("idx_step_execution_id", "execution_id"),
        Index("idx_step_node_id", "node_id"),
        Index("idx_step_status", "status"),
    )


class Trigger(Base):
    """Trigger model - represents workflow triggers (manual, webhook, cron)."""
    
    __tablename__ = "triggers"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # manual | webhook | cron
    enabled = Column(Boolean, default=True, nullable=False)
    config = Column(JSON, nullable=True)
    last_fired_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="triggers")
    
    __table_args__ = (
        Index("idx_trigger_workflow_id", "workflow_id"),
        Index("idx_trigger_type", "type"),
        Index("idx_trigger_enabled", "enabled"),
        Index("idx_trigger_next_run_at", "next_run_at"),
    )


class JobQueue(Base):
    """JobQueue model - persistent job queue backed by PostgreSQL."""

    __tablename__ = "job_queue"

    id = Column(String, primary_key=True)
    execution_id = Column(String, nullable=False)
    node_id = Column(String, nullable=False)
    node_label = Column(String, nullable=False)
    node_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending | processing | completed | failed
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    locked_at = Column(DateTime, nullable=True)
    locked_by = Column(String, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_job_queue_status", "status"),
        Index("idx_job_queue_execution_id", "execution_id"),
        Index("idx_job_queue_created_at", "created_at"),
    )


class AuditLog(Base):
    """AuditLog model - audit trail for all system events."""

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    event = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_audit_event", "event"),
        Index("idx_audit_entity_type", "entity_type"),
        Index("idx_audit_entity_id", "entity_id"),
        Index("idx_audit_created_at", "created_at"),
    )

