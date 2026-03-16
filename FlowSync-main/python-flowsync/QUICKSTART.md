# FlowSync Python - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites

Ensure you have:
- Python 3.11+ installed
- PostgreSQL 14+ running
- Git (optional)

### 2. Install Dependencies

```bash
cd python-flowsync

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Minimum required: DATABASE_URL
```

Example `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/flowsync
APP_PORT=8000
DEBUG=true
```

### 4. Initialize Database

```bash
# Create database tables
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

Or manually in PostgreSQL:
```sql
CREATE DATABASE flowsync;
```

### 5. Start the Server

```bash
python run.py
```

You should see:
```
🚀 Starting FlowSync Python
============================================================
Environment: development
Host: 0.0.0.0:8000
Worker Concurrency: 5
Scheduler: Enabled
============================================================
✅ Registered 9 worker handlers: start, end, action, delay, condition, fork, join, transform, webhook_response
🚀 FlowSync Python starting...
✅ Job consumer started
✅ Scheduler started
```

### 6. Test the API

Open your browser or use curl:

```bash
# Health check
curl http://localhost:8000/api/health

# API documentation (Swagger UI)
open http://localhost:8000/docs
```

### 7. Create Your First Workflow

```bash
curl -X POST http://localhost:8000/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hello World Workflow",
    "description": "My first workflow",
    "definitionJson": {
      "nodes": [
        {"id": "1", "type": "start", "label": "Start", "config": {}},
        {"id": "2", "type": "delay", "label": "Wait 1s", "config": {"delayMs": 1000}},
        {"id": "3", "type": "end", "label": "End", "config": {}}
      ],
      "edges": [
        {"id": "e1", "source": "1", "target": "2"},
        {"id": "e2", "source": "2", "target": "3"}
      ]
    }
  }'
```

### 8. Execute the Workflow

```bash
# Get workflow ID from previous response, then:
curl -X POST http://localhost:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "YOUR_WORKFLOW_ID",
    "input": {"message": "Hello FlowSync!"}
  }'
```

### 9. Check Execution Status

```bash
# Get execution ID from previous response, then:
curl http://localhost:8000/api/executions/YOUR_EXECUTION_ID
```

## 📚 Next Steps

- **Explore API**: Visit http://localhost:8000/docs for interactive API documentation
- **Create Complex Workflows**: Add conditions, forks, joins, and HTTP actions
- **Set Up Webhooks**: Create webhook triggers for external integrations
- **Schedule Workflows**: Use cron triggers for periodic execution
- **Monitor System**: Check `/api/health` and `/api/queue` endpoints

## 🔧 Troubleshooting

### Database Connection Error
```
Ensure PostgreSQL is running and DATABASE_URL is correct
```

### Port Already in Use
```
Change APP_PORT in .env to a different port (e.g., 8001)
```

### Import Errors
```
Make sure virtual environment is activated and dependencies are installed
```

## 📖 Learn More

- Read the full [README.md](README.md)
- Check the [API documentation](http://localhost:8000/docs)
- Explore example workflows in the `/examples` directory (coming soon)

---

**Happy Orchestrating! 🎉**

