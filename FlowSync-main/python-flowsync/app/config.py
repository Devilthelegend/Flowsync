"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/flowsync"
    
    # Clerk Authentication
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    
    # Application
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # Worker Configuration
    max_worker_concurrency: int = 5
    worker_poll_interval_ms: int = 500
    
    # Queue Configuration
    job_queue_max_retries: int = 3
    job_queue_backoff_ms: int = 1000
    job_queue_backoff_multiplier: int = 2
    
    # Scheduler
    scheduler_enabled: bool = True
    scheduler_interval_seconds: int = 60
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()

