# FlowSync - Workflow Orchestration Engine

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A production-ready workflow orchestration engine built with modern Python technologies.**

FlowSync is a durable workflow orchestration system that enables you to design, execute, and monitor complex business processes as directed acyclic graphs (DAGs) with automatic retries, parallel execution, and full observability.

---

## 🎯 Project Overview

This project demonstrates advanced backend development skills including:

- **Distributed Systems Design** - PostgreSQL-backed job queue with row-level locking
- **Event-Driven Architecture** - Microkernel pattern with pluggable handlers
- **Async Programming** - Full async/await implementation using Python asyncio
- **Algorithm Implementation** - Kahn's topological sort for DAG validation
- **Database Design** - Normalized schema with proper indexing and relationships
- **API Design** - RESTful API with auto-generated OpenAPI documentation
- **Reliability Engineering** - Retry logic, exponential backoff, and fault tolerance

---

## ✨ Key Features

- 🔄 **Durable Execution** - PostgreSQL-backed persistent queue survives restarts
- 🔁 **Automatic Retries** - Exponential backoff with configurable attempts
- ⚡ **Parallel Processing** - Fork/join nodes for concurrent execution
- 🌿 **Conditional Branching** - Dynamic workflow paths based on runtime conditions
- 📅 **Multiple Triggers** - Manual, webhook, and cron-based scheduling
- 🔍 **Full Observability** - Health checks, metrics, and complete audit trails
- 🚀 **REST API** - Complete CRUD operations with interactive documentation
- 🏗️ **Extensible** - Plugin-based handler system for custom node types

---

## 🏗️ Architecture Highlights

### Event-Driven Microkernel Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                           │
│         (REST API, Webhooks, Cron Triggers)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   API GATEWAY (FastAPI)                     │
│    Workflows • Executions • Triggers • Webhooks • Health    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  ORCHESTRATION LAYER                        │
│    DAG Validator • Execution Engine • Cron Scheduler        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              JOB QUEUE (PostgreSQL)                         │
│      SELECT FOR UPDATE SKIP LOCKED (Row Locking)            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    WORKER LAYER                             │
│    Job Consumer (5 concurrent) + 9 Handler Types            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              PERSISTENCE (PostgreSQL)                       │
│    Workflows • Executions • Steps • Triggers • Queue        │
└─────────────────────────────────────────────────────────────┘
```

[📖 View Full Architecture Documentation](python-flowsync/docs/ARCHITECTURE.md)

---

## 🚀 Quick Start

```bash
# Navigate to project
cd python-flowsync

# Run automated setup (Windows)
START_HERE.bat

# Or manual setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**Access the application:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

[📖 Detailed Setup Guide](python-flowsync/QUICKSTART.md)

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | FastAPI 0.115+ | High-performance async web framework |
| **Language** | Python 3.11+ | Modern Python with type hints |
| **Database** | PostgreSQL 14+ | ACID-compliant persistence + job queue |
| **ORM** | SQLAlchemy 2.0 | Async database operations |
| **Validation** | Pydantic 2.0 | Request/response validation |
| **Server** | Uvicorn | ASGI server |

---

## 🎯 Technical Highlights for Interviews

### System Design
- ✅ **Microkernel Architecture** - Extensible core with pluggable handlers
- ✅ **Event-Driven Design** - Asynchronous job processing
- ✅ **Distributed Queue** - PostgreSQL with `SELECT FOR UPDATE SKIP LOCKED`

### Algorithms & Data Structures
- ✅ **DAG Validation** - Kahn's topological sort for cycle detection
- ✅ **Graph Traversal** - BFS for workflow execution
- ✅ **Exponential Backoff** - Smart retry strategy

### Database Design
- ✅ **6-Table Schema** - Normalized with proper relationships
- ✅ **Row-Level Locking** - Distributed coordination
- ✅ **ACID Compliance** - Transactional integrity

### Software Engineering
- ✅ **Type Safety** - Full type hints with Pydantic
- ✅ **Clean Architecture** - Separation of concerns
- ✅ **API Design** - RESTful with OpenAPI docs
- ✅ **Async/Await** - Non-blocking I/O throughout

---

## 📚 Documentation

- [📖 Architecture Overview](python-flowsync/docs/ARCHITECTURE.md) - System design and patterns
- [🚀 Quick Start Guide](python-flowsync/QUICKSTART.md) - Get started in 5 minutes
- [🔄 Migration Guide](python-flowsync/docs/MIGRATION_GUIDE.md) - Node.js to Python comparison
- [📁 Project Structure](python-flowsync/docs/STRUCTURE.md) - File organization
- [🤝 Contributing](python-flowsync/CONTRIBUTING.md) - How to contribute

---

## 📝 License

MIT License - See [LICENSE](python-flowsync/LICENSE) file for details

---

## 👨‍💻 About

Built as a demonstration of modern Python backend development practices, showcasing:
- Distributed systems design
- Event-driven architecture
- Async programming patterns
- Database optimization
- API design best practices

**Tech Stack**: FastAPI • PostgreSQL • SQLAlchemy • Pydantic • asyncio

---

⭐ **If you find this project interesting, please star the repository!**

