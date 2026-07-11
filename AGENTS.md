# AGENTS.md — JobPulse

Instructions for AI assistants working on this project.

## Stack

- Backend: Python 3.13 + uv
- Frontend: Node 24 LTS + pnpm
- Scraper: Python 3.13 + uv
- Containers: Docker Compose

## Code Style

- Python: Ruff (compatible with Black), line-length 88
- TypeScript: strict mode
- No comments unless they add value
- Use semantic variable/function names in English
- Follow existing patterns in the codebase

## Commands

- Lint (Python): `ruff check .`
- Format (Python): `ruff format .`
- Test (backend): `uv run pytest`
- Test (scraper): `uv run pytest`

## Project Structure

- `/backend` — FastAPI application
- `/frontend` — React + Vite application
- `/scraper` — Data collection workers
- `/docs` — Documentation
- `/.github/workflows` — CI/CD pipelines

## Rules

- Respond in neutral Spanish (espanol latino neutro)
- No emojis, emoticons, or regional slang
- Explain technical decisions concisely
- Do not add dependencies without asking
- Do not generate lockfiles
- Do not install frameworks before their sprint

## Architecture Rules

- Every new feature must be integrated through the API router hierarchy (`main.py` should remain minimal and never contain endpoint definitions).
- No endpoint without tests.

## Status

### Done
- Scaffold: monorepo, .gitignore, LICENSE, docker-compose, pre-commit
- Backend: FastAPI + create_app() factory, /api/v1/health endpoint
- Persistence: SQLAlchemy 2 async, psycopg, Alembic async, PostgreSQL in Docker
- Database engine: session.py (create_engine, get_db), lifespan with dispose
- Tests: health (3), database connection (1), repositories (6), scrapers (3) — all passing
- Settings: DATABASE_URL required, injected via create_app(settings)
- Declarative base: Base(DeclarativeBase) in app/db/base.py
- ORM models: `Company` y `Job` con enums (`EmploymentType`, `ExperienceLevel`, `Source`), relaciones e indices (`app/models/`)
- Pydantic schemas: `JobCreate`/`Update`/`Response`, `CompanyCreate`/`Update`/`Response` (`app/schemas/`)
- Repository layer: `RepositoryBase` generico + `JobRepository` y `CompanyRepository` (`app/repositories/`)
- CRUD endpoints: `/api/v1/jobs` y `/api/v1/companies` con operaciones completas
- Alembic migration inicial: `0001_init_models.py` (tablas `companies`, `jobs`, tipos ENUM)
- Scraper GetOnBoard integrado en backend (`app/scrapers/`), con servicio de persistencia

### Pending
- Frontend (React + Vite)
- Scraper externo (`/scraper`) con Playwright
- Authentication
- CI/CD pipelines
