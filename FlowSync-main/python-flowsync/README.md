# FlowSync - Workflow Orchestration Engine

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A production-ready workflow orchestration engine built with FastAPI and PostgreSQL.**

FlowSync enables you to design, execute, and monitor complex workflows as directed acyclic graphs (DAGs) with full durability, automatic retries, and parallel execution.

## ✨ Key Features

- 🔄 **Durable Execution** - PostgreSQL-backed job queue with row-level locking
- 🔁 **Automatic Retries** - Exponential backoff with configurable attempts
- ⚡ **Parallel Processing** - Fork/join nodes for concurrent execution
- 🌿 **Conditional Branching** - Dynamic workflow paths based on runtime conditions
- 📅 **Multiple Triggers** - Manual, webhook, and cron-based scheduling
- 🔍 **Full Observability** - Health checks, metrics, and audit trails
- 🚀 **REST API** - Complete CRUD operations with auto-generated docs
- 🏗️ **Extensible Architecture** - Plugin-based handler system

## 🏗️ Architecture

FlowSync implements an **event-driven microkernel architecture**:

- **API Gateway** (FastAPI) - REST endpoints with auto-generated OpenAPI docs
- **Orchestration Layer** - DAG validator + execution engine + cron scheduler
- **Job Queue** (PostgreSQL) - Persistent queue with `SELECT FOR UPDATE SKIP LOCKED`
- **Worker Layer** - Async job consumer with 9 pluggable handlers
- **Persistence** (PostgreSQL) - 6 tables with ACID compliance

[📖 View Full Architecture Documentation](docs/ARCHITECTURE.md)

## 🎯 Supported Node Types

| Type | Purpose | Use Case |
|------|---------|----------|
| **start** | Entry point | Initialize workflow |
| **end** | Terminal node | Complete workflow |
| **action** | HTTP requests | Call external APIs |
| **condition** | Branching logic | if/else decisions |
| **delay** | Time delays | Wait before next step |
| **fork** | Parallel split | Process multiple branches |
| **join** | Parallel merge | Wait for all branches |
| **transform** | Data manipulation | JSONPath, custom scripts |
| **webhook_response** | HTTP reply | Respond to webhooks |

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | FastAPI 0.115+ | High-performance async web framework |
| **Language** | Python 3.11+ | Modern Python with type hints |
| **Database** | PostgreSQL 14+ | ACID-compliant persistence + job queue |
| **ORM** | SQLAlchemy 2.0 | Async database operations |
| **Validation** | Pydantic 2.0 | Request/response validation |
| **Scheduling** | croniter | Cron expression parsing |
| **HTTP Client** | httpx | Async HTTP requests |
| **Server** | Uvicorn | ASGI server |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip

### Installation

**Option 1: Automated Setup (Windows)**
```bash
START_HERE.bat
```

**Option 2: Manual Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit DATABASE_URL in .env

# Initialize database
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

# Start server
python run.py
```

### Access the Application

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

[📖 Detailed Setup Guide](QUICKSTART.md)

## ⚙️ Configuration

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/flowsync

# Application
APP_PORT=8000
APP_ENV=development
DEBUG=true

# Worker Configuration
MAX_WORKER_CONCURRENCY=5

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_SECONDS=60

# Authentication (optional)
CLERK_SECRET_KEY=your_clerk_secret_key
```

## 📚 API Endpoints

### Workflows
- `GET /api/workflows` - List workflows
- `POST /api/workflows` - Create workflow
- `GET /api/workflows/{id}` - Get workflow
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow

### Executions
- `GET /api/executions` - List executions
- `POST /api/executions` - Start execution
- `GET /api/executions/{id}` - Get execution details
- `POST /api/executions/{id}/cancel` - Cancel execution

### Triggers
- `GET /api/triggers` - List triggers
- `POST /api/triggers` - Create trigger
- `PUT /api/triggers/{id}` - Update trigger
- `DELETE /api/triggers/{id}` - Delete trigger

### Webhooks
- `POST /api/webhooks/{trigger_id}` - Webhook ingestion

### System
- `GET /api/health` - Health check
- `GET /api/queue` - Queue status
- `GET /api/observability/metrics` - Metrics
- `GET /api/observability/audit` - Audit logs

## 📁 Project Structure

```
flowsync/
├── app/
│   ├── api/                 # REST API endpoints (7 routers)
│   ├── queue/               # Job queue system
│   ├── workers/             # Worker handlers (9 types)
│   ├── scheduler/           # Cron scheduler
│   ├── main.py              # FastAPI application
│   ├── orchestrator.py      # Execution engine
│   ├── dag_validator.py     # DAG validation
│   └── models.py            # Database models
├── docs/                    # Documentation
├── requirements.txt         # Dependencies
└── run.py                   # Entry point
```

[📖 View Detailed Structure](docs/STRUCTURE.md)

## 🧪 Example Workflow

```json
{
  "name": "HTTP Request Workflow",
  "description": "Fetch data from API and process it",
  "definitionJson": {
    "nodes": [
      {"id": "1", "type": "start", "label": "Start", "config": {}},
      {"id": "2", "type": "action", "label": "Fetch Data", "config": {
        "actionType": "http",
        "method": "GET",
        "url": "https://api.example.com/data"
      }},
      {"id": "3", "type": "transform", "label": "Process", "config": {
        "transformType": "jsonpath",
        "path": "$.data"
      }},
      {"id": "4", "type": "end", "label": "End", "config": {}}
    ],
    "edges": [
      {"id": "e1", "source": "1", "target": "2"},
      {"id": "e2", "source": "2", "target": "3"},
      {"id": "e3", "source": "3", "target": "4"}
    ]
  }
}
```

## 🎯 Key Technical Highlights

### For Recruiters & Interviewers:

- ✅ **Event-Driven Architecture** - Microkernel pattern with pluggable handlers
- ✅ **Distributed Systems** - PostgreSQL-backed queue with row-level locking
- ✅ **Async Programming** - Full async/await with Python asyncio
- ✅ **Algorithm Implementation** - Kahn's topological sort for DAG validation
- ✅ **Database Design** - 6-table schema with proper indexing and relationships
- ✅ **API Design** - RESTful API with auto-generated OpenAPI documentation
- ✅ **Reliability Patterns** - Retry logic, exponential backoff, stale lock recovery
- ✅ **Scalability** - Horizontally scalable, stateless API layer
- ✅ **Code Quality** - Type hints, Pydantic validation, clean architecture

## 📊 Monitoring

```bash
# Health check
curl http://localhost:8000/api/health

# Queue status
curl http://localhost:8000/api/queue

# Interactive API docs
open http://localhost:8000/docs
```

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - System design and patterns
- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Migration Guide](docs/MIGRATION_GUIDE.md) - Node.js to Python comparison
- [Project Structure](docs/STRUCTURE.md) - File organization

## 🔒 Security Considerations

- ⚠️ Condition and transform nodes use `eval()` - sandbox in production
- 🔐 Add rate limiting for production deployments
- 🔑 Use environment variables for sensitive data
- 🛡️ Implement proper authentication (Clerk integration ready)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👨‍💻 Author

Built as a demonstration of modern Python backend development practices.

**Tech Stack**: FastAPI • PostgreSQL • SQLAlchemy • Pydantic • asyncio

---

⭐ **Star this repo if you find it useful!**

