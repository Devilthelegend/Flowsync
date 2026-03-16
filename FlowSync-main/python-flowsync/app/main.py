"""FlowSync Python - Main FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import workflows, executions, triggers, webhooks, health, observability, queue_routes
from app.queue.job_consumer import start_consumer, stop_consumer
from app.scheduler.scheduler import scheduler

# Import to register handlers
import app.workers.register_handlers  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - startup and shutdown events."""
    # Startup
    print("🚀 FlowSync Python starting...")
    
    # Start job consumer
    start_consumer()
    print("✅ Job consumer started")
    
    # Start scheduler if enabled
    if settings.scheduler_enabled:
        scheduler.start()
        print("✅ Scheduler started")
    
    yield
    
    # Shutdown
    print("🛑 FlowSync Python shutting down...")
    
    # Stop consumer
    await stop_consumer()
    print("✅ Job consumer stopped")
    
    # Stop scheduler
    if settings.scheduler_enabled:
        scheduler.stop()
        print("✅ Scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="FlowSync",
    description="Durable Workflow Orchestration Engine",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(executions.router, prefix="/api/executions", tags=["executions"])
app.include_router(triggers.router, prefix="/api/triggers", tags=["triggers"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(observability.router, prefix="/api/observability", tags=["observability"])
app.include_router(queue_routes.router, prefix="/api/queue", tags=["queue"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "FlowSync Python",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.app_env,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )

