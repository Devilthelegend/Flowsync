# Contributing to FlowSync

Thank you for your interest in contributing to FlowSync!

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/flowsync.git
   cd flowsync
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up pre-commit hooks (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for public APIs
- Keep functions focused and small

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Submitting Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request

## Adding New Node Types

To add a new node type handler:

1. Create a new file in `app/workers/handlers/`
2. Implement the handler class with `type` and `execute()` method
3. Register it in `app/workers/register_handlers.py`

Example:
```python
from app.workers.worker_types import WorkerJob, WorkerResult

class MyCustomHandler:
    type = "my_custom"
    
    async def execute(self, job: WorkerJob) -> WorkerResult:
        # Your logic here
        return WorkerResult(
            success=True,
            output={"result": "success"}
        )
```

## Questions?

Feel free to open an issue for any questions or suggestions!

