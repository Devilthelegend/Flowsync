"""Run script to start FlowSync Python server."""

import uvicorn
from app.config import settings

# Import to register handlers
import app.workers.register_handlers  # noqa

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting FlowSync Python")
    print("=" * 60)
    print(f"Environment: {settings.app_env}")
    print(f"Host: {settings.app_host}:{settings.app_port}")
    print(f"Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'configured'}")
    print(f"Worker Concurrency: {settings.max_worker_concurrency}")
    print(f"Scheduler: {'Enabled' if settings.scheduler_enabled else 'Disabled'}")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

