"""Setup script for FlowSync Python."""

from setuptools import setup, find_packages

setup(
    name="flowsync-python",
    version="1.0.0",
    description="Durable Workflow Orchestration Engine",
    author="FlowSync Team",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "sqlalchemy>=2.0.36",
        "asyncpg>=0.30.0",
        "psycopg2-binary>=2.9.10",
        "alembic>=1.14.0",
        "pydantic>=2.10.3",
        "pydantic-settings>=2.6.1",
        "httpx>=0.28.1",
        "croniter>=5.0.1",
        "apscheduler>=3.10.4",
        "python-dotenv>=1.0.1",
        "structlog>=24.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.4",
            "pytest-asyncio>=0.24.0",
            "black>=24.10.0",
            "ruff>=0.8.4",
            "mypy>=1.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "flowsync=run:main",
        ],
    },
)

