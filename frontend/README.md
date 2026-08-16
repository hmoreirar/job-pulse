# JobPulse Frontend

Web application for the JobPulse platform. Built with React, TypeScript, and Vite.

## Stack

- React 18
- TypeScript (strict mode)
- Vite 5

## Getting Started

```bash
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` and proxies `/api` to the backend
(`http://127.0.0.1:8000`), so the backend must be running:

```bash
cd ../backend
uv run uvicorn app.main:create_app --factory --reload
```

To point the proxy at a different backend (e.g. `VITE_API_PROXY_TARGET=http://127.0.0.1:8010`).

## Scripts

- `npm run dev` — start the dev server with hot reload
- `npm run build` — type-check and build for production
- `npm run typecheck` — run the TypeScript compiler
- `npm run preview` — preview the production build

## Structure

```
src/
├── api/          # HTTP client and API calls
├── components/   # React components (JobList, JobCard, JobFilters, Pagination)
├── hooks/        # Data fetching hooks
├── lib/          # Labels and formatting helpers
├── styles/       # Global styles
└── types/        # TypeScript types matching the backend schemas
```
