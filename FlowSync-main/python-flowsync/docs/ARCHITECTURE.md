# FlowSync - System Architecture

## 🏗️ High-Level Architecture

FlowSync is a **Durable Workflow Orchestration Engine** built on a **microkernel architecture** with **event-driven job processing**.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  (REST API Clients, Webhooks, Cron Triggers, Web Browsers)     │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│                    (FastAPI Application)                        │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │Workflows │Executions│ Triggers │ Webhooks │  Health  │      │
│  │   API    │   API    │   API    │   API    │   API    │      │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘      │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    ORCHESTRATION LAYER                          │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  DAG Validator  │  │ Orchestrator │  │   Scheduler     │   │
│  │ (Cycle Check)   │  │   Engine     │  │ (Cron Triggers) │   │
│  └─────────────────┘  └──────────────┘  └─────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      JOB QUEUE LAYER                            │
│              (PostgreSQL-backed Persistent Queue)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SELECT FOR UPDATE SKIP LOCKED (Row-Level Locking)       │  │
│  │  • Enqueue Jobs  • Dequeue Jobs  • Retry Logic           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      WORKER LAYER                               │
│                   (Job Consumer + Handlers)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Job Consumer (Async Worker Pool - 5 concurrent tasks)   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌────┬────┬────┬────┬────┬────┬────┬────┬────┐              │
│  │Start│End │Act │Cond│Dely│Fork│Join│Tran│Webh│ (9 Handlers)│
│  └────┴────┴────┴────┴────┴────┴────┴────┴────┘              │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    PERSISTENCE LAYER                            │
│                      (PostgreSQL 14+)                           │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐     │
│  │Workflows │Executions│  Steps   │ Triggers │JobQueue  │     │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Architecture Pattern

**Pattern**: **Event-Driven Microkernel Architecture**

### Core Components:

1. **Microkernel** = Orchestrator + DAG Validator
2. **Plugins** = 9 Worker Handlers (extensible)
3. **Event Bus** = PostgreSQL Job Queue
4. **Persistence** = PostgreSQL Database

---

## 📦 Layer-by-Layer Breakdown

### 1️⃣ **API Gateway Layer** (FastAPI)

**Purpose**: HTTP interface for external clients

**Components**:
- **7 REST API Routers**:
  - Workflows API - CRUD operations
  - Executions API - Start, monitor, cancel
  - Triggers API - Manual, webhook, cron
  - Webhooks API - External event ingestion
  - Health API - System health checks
  - Observability API - Metrics & audit logs
  - Queue API - Queue monitoring

**Technology**: FastAPI with async/await

**Key Features**:
- Auto-generated OpenAPI docs
- Pydantic validation
- CORS middleware
- Async request handling

---

### 2️⃣ **Orchestration Layer**

**Purpose**: Workflow logic and scheduling

**Components**:

#### A. **DAG Validator**
- **Algorithm**: Kahn's Topological Sort
- **Checks**:
  - Duplicate node IDs
  - Start/end node existence
  - Edge reference validation
  - Cycle detection
  - Reachability analysis
  - Fork/join structural validation

#### B. **Orchestrator Engine**
- **Responsibilities**:
  - Create execution records
  - Find initial nodes (nodes with no incoming edges)
  - Publish jobs to queue
  - Handle execution cancellation
  - Track execution status

#### C. **Scheduler**
- **Type**: Cron-based scheduler
- **Technology**: croniter + APScheduler
- **Function**: Automatically trigger workflows based on cron expressions

---

### 3️⃣ **Job Queue Layer** (PostgreSQL-backed)

**Purpose**: Durable, distributed job queue

**Implementation**:
```sql
SELECT * FROM job_queue
WHERE status = 'pending'
  AND (locked_at IS NULL OR locked_at < NOW() - INTERVAL '5 minutes')
ORDER BY created_at ASC
LIMIT 1
FOR UPDATE SKIP LOCKED;
```

**Key Features**:
- **Row-level locking** - Prevents duplicate processing
- **SKIP LOCKED** - Enables concurrent workers
- **Retry logic** - Exponential backoff (3 attempts)
- **Stale lock recovery** - Handles worker crashes

**Queue Operations**:
- `enqueue()` - Add job to queue
- `dequeue()` - Get next pending job (with lock)
- `mark_done()` - Mark job as completed
- `mark_failed()` - Mark job as failed

---

### 4️⃣ **Worker Layer**

**Purpose**: Execute workflow nodes

**Architecture**: **Handler Registry Pattern**

#### A. **Job Consumer**
- **Type**: Async worker pool
- **Concurrency**: 5 concurrent tasks (configurable)
- **Polling**: 500ms interval
- **Retry**: Exponential backoff (1s, 2s, 4s)

#### B. **9 Worker Handlers**

| Handler | Purpose | Example |
|---------|---------|---------|
| **start** | Entry point | Initialize workflow |
| **end** | Terminal node | Complete workflow |
| **action** | HTTP requests | Call external APIs |
| **condition** | Branching | if/else logic |
| **delay** | Time delays | Wait 5 seconds |
| **fork** | Parallel split | Process A & B concurrently |
| **join** | Parallel merge | Wait for A & B to complete |
| **transform** | Data transformation | JSONPath, custom scripts |
| **webhook_response** | Webhook reply | Send HTTP response |

**Handler Interface**:
```python
class NodeHandler:
    type: str  # Node type identifier
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        # Execute node logic
        pass
```

---

### 5️⃣ **Persistence Layer** (PostgreSQL)

**Purpose**: Durable storage

**Database Schema** (6 tables):

1. **workflows** - Workflow definitions
2. **executions** - Workflow execution instances
3. **step_executions** - Individual node executions
4. **triggers** - Workflow triggers (manual, webhook, cron)
5. **job_queue** - Persistent job queue
6. **audit_logs** - Audit trail

**Technology**: SQLAlchemy 2.0 (async mode with asyncpg)

---

## 🔄 Execution Flow

### Workflow Execution Lifecycle:

```
1. API Request
   POST /api/executions
   { workflowId, input }
   
2. Orchestrator
   ├─ Validate workflow exists
   ├─ Create execution record
   ├─ Find initial nodes (no incoming edges)
   └─ Publish jobs to queue
   
3. Job Queue
   ├─ Store jobs in PostgreSQL
   └─ Return job IDs
   
4. Job Consumer (polling loop)
   ├─ Dequeue next job (with lock)
   ├─ Find handler by node type
   ├─ Execute handler
   └─ Process result
   
5. Handler Execution
   ├─ Execute node logic
   ├─ Return success/failure
   └─ Return output data
   
6. Result Processing
   ├─ Mark job as done/failed
   ├─ Update step_execution record
   ├─ Find next nodes (follow edges)
   ├─ Publish next jobs to queue
   └─ If no more nodes → mark execution complete
```

---

## 🧩 Design Patterns Used

### 1. **Microkernel Architecture**
- Core: Orchestrator + DAG Validator
- Plugins: Worker Handlers (extensible)

### 2. **Registry Pattern**
- Handler Registry maps node types to handlers
- Allows dynamic handler registration

### 3. **Event-Driven Architecture**
- Jobs are events in the queue
- Workers react to events asynchronously

### 4. **Repository Pattern**
- Database access abstracted through SQLAlchemy ORM
- Async session management

### 5. **Strategy Pattern**
- Each handler implements the same interface
- Different execution strategies per node type

### 6. **Producer-Consumer Pattern**
- Orchestrator = Producer (publishes jobs)
- Job Consumer = Consumer (processes jobs)

---

## 🔐 Concurrency & Reliability

### Concurrency Model:
- **Python asyncio** - Single-threaded event loop
- **PostgreSQL locking** - Distributed coordination
- **Worker pool** - 5 concurrent async tasks

### Reliability Features:
- ✅ **Durable queue** - PostgreSQL persistence
- ✅ **Retry logic** - Exponential backoff
- ✅ **Stale lock recovery** - Handles worker crashes
- ✅ **Atomic operations** - Database transactions
- ✅ **Idempotency** - Job IDs prevent duplicates

---

## 📊 Data Flow

```
User Input → API → Orchestrator → Job Queue → Worker → Database
                                      ↑                    ↓
                                      └────────────────────┘
                                    (Next jobs published)
```

---

## 🚀 Scalability Considerations

### Current Architecture:
- **Single process** - One FastAPI instance
- **Async I/O** - Handles many concurrent requests
- **PostgreSQL queue** - Shared across instances

### Horizontal Scaling:
- ✅ Run multiple FastAPI instances
- ✅ All share same PostgreSQL database
- ✅ Queue locking prevents duplicate work
- ✅ Stateless API layer

### Vertical Scaling:
- Increase `MAX_WORKER_CONCURRENCY`
- Increase PostgreSQL connection pool
- Add database read replicas

---

## 🎓 How to Explain to Others

### **Elevator Pitch** (30 seconds):
> "FlowSync is a workflow orchestration engine that lets you define complex business processes as directed graphs. It uses PostgreSQL as a durable job queue and executes workflows reliably with retry logic and parallel processing."

### **Technical Explanation** (2 minutes):
> "It's built on a microkernel architecture where the core orchestrator validates and executes DAGs. When you start a workflow, it creates an execution record, finds the initial nodes, and publishes jobs to a PostgreSQL-backed queue. Worker processes poll the queue using row-level locking to prevent duplicates, execute the appropriate handler for each node type, and publish the next jobs. This continues until all nodes are complete. The system supports 9 node types including HTTP actions, conditional branching, parallel execution with fork/join, and time delays."

### **Business Explanation** (1 minute):
> "FlowSync automates complex business workflows. For example, you could create a workflow that: receives a webhook when a customer signs up, calls an external API to verify their email, waits 24 hours, sends a welcome email, and logs everything to your CRM. If any step fails, it automatically retries. You can trigger workflows manually, via webhooks, or on a schedule."

---

**Architecture Type**: Event-Driven Microkernel with Persistent Queue  
**Deployment Model**: Monolithic (can be horizontally scaled)  
**Concurrency Model**: Async I/O with distributed locking  
**Persistence**: PostgreSQL (ACID compliant)

