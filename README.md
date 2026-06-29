# JobPulse

Job market intelligence platform. Collect, analyze, and visualize IT job listings to uncover trends and insights.

## Objectives

- Aggregate job listings from multiple sources into a single searchable database
- Detect salary trends, in-demand skills, and market shifts over time
- Provide a clean dashboard for exploring the data interactively
- Automate data collection on a scheduled basis

## Architecture

```
┌────────────┐     ┌──────────────┐     ┌───────────┐
│  Scraper   │────▶│   Backend    │────▶│ Frontend  │
│ (Playwright)│    │  (FastAPI)   │    │ (React)   │
└────────────┘     └──────┬───────┘     └───────────┘
                          │
                    ┌─────▼──────┐
                    │ PostgreSQL │
                    └────────────┘
```

- **Scraper** — Playwright-based workers that collect data from job boards
- **Backend** — REST API that serves data to the frontend
- **Frontend** — React SPA for data visualization and search

## Tech Stack

| Layer       | Technology                                       |
|-------------|--------------------------------------------------|
| Backend     | Python 3.13, FastAPI, PostgreSQL                  |
| Frontend    | Node 24, React, TypeScript, Vite                 |
| Scraper     | Python 3.13, Playwright                          |
| Infra       | Docker Compose, GitHub Actions                   |
| Code style  | Ruff (Python), Prettier (frontend, TBD)          |

## Project Structure

```
jobpulse/
├── backend/         # REST API
├── frontend/        # Web application
├── scraper/         # Data collection workers
├── docs/            # Documentation
└── .github/workflows/  # CI/CD pipelines
```

## Roadmap

1. **Sprint 1** — Project scaffold (this sprint)
2. **Sprint 2** — Basic scraper with Playwright on a single source
3. **Sprint 3** — REST API with FastAPI and PostgreSQL
4. **Sprint 4** — Frontend with React, Vite, and basic dashboard
5. **Sprint 5** — CI/CD pipelines, Docker Compose, deployment

## License

MIT License — see [LICENSE](LICENSE).
