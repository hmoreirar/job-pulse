# JobPulse Backend

REST API for the JobPulse platform. Built with Python and FastAPI.

## Getting Started

```bash
uv venv
source .venv/bin/activate
uv sync
uv run uvicorn app.main:create_app --factory --reload
```

Open http://localhost:8000/docs for interactive documentation.

## Tests

```bash
uv run pytest -v
```
