<!-- GSD:project-start source:PROJECT.md -->
## Project

**Reverso Signal Dashboard**

A web dashboard for uploading time series CSV signals and generating predictions using the Reverso foundation model. Users upload CSV files, configure prediction parameters (context size, prediction length, frequency), and visualize forecast results with interactive D3.js charts. Designed for data scientists and analysts working with large-scale time series data (50K+ points).

**Core Value:** Upload any time series CSV and get a Reverso-powered forecast in seconds with full control over prediction parameters.

### Constraints

- **Tech Stack**: shadcn frontend, FastAPI backend, uv for Python dependencies — as specified
- **GPU Required**: Reverso inference needs CUDA-compatible GPU — not a CPU-only tool
- **Scale**: Must handle 50K+ point signals efficiently
- **Language**: Implementation in English, user communicates in Spanish
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **FastAPI** | 0.128.x | REST API backend | High performance, async-first, automatic OpenAPI docs, native `UploadFile` support for CSV handling. `fastapi run` includes Uvicorn with proper lifespan events. |
| **Uvicorn** | bundled with FastAPI | ASGI server | FastAPI's `fastapi run` uses uvicorn under the hood. Use `--workers 4` for production. |
| **Python** | 3.12+ | Runtime | Required for latest FastAPI. 3.12 has significant performance improvements with faster startup and better memory. |
### Frontend
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Next.js** | 15.x (App Router) | React framework | App Router is the current standard. Server Components reduce client bundle. File-based routing, API routes for proxying. |
| **shadcn/ui** | 0.9.x | UI component library | Copy-paste components (not a package), built on Radix UI primitives + Tailwind CSS. Full customization, no package lock-in. |
| **Tailwind CSS** | 4.x | Utility CSS | First-class shadcn support. JIT mode, tree-shaking. |
| **D3.js** | v7 | Time series visualization | Required per project constraints. Full control over chart behavior, zoom/pan support via `d3-zoom`. |
| **TypeScript** | 5.x | Type safety | Required for shadcn/ui. Catches errors at build time. |
### Time Series Model
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **PyTorch** | 2.x | Model runtime | Reverso and most time series transformers are PyTorch models. CUDA-compatible for GPU inference. |
| **Reverso** | (unverified) | Forecasting model | **NOTE:** Public GitHub repo not found at `SalesforceAIResearch/Reverso`. Verify model availability before implementation. Closest reference: `uni2ts` (Moirai) from same org. |
| **pandas** | 2.x | CSV processing | Fast CSV parsing for 50K+ row files. `pd.read_csv()` with chunking for memory management. |
| **numpy** | 1.x | Array operations | Required for model input preparation, normalization to [0,1]. |
### Package Management
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **uv** | latest | Python package manager | 10-100x faster than pip. Used as specified in project constraints. Replaces pip, poetry, pip-tools. |
| **npm** | 10.x | Node package manager | Standard for Next.js projects. |
| **pnpm** | 9.x | Node package manager (optional) | Faster, more efficient storage. Works with shadcn/cli. |
### Infrastructure
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Docker** | 25.x | Containerization | FastAPI runs in a container. CUDA support via `nvidia/cuda` base images for GPU inference. |
| **docker-compose** | 2.x | Multi-container orchestration | Coordinates FastAPI + frontend containers. `docker compose watch` for dev workflow. |
| **NVIDIA Container Toolkit** | latest | GPU access in Docker | Required for running PyTorch models with CUDA in containers. |
## Alternatives Considered
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backend framework | FastAPI | Flask | Flask lacks async native support; would require `asyncpg`/`aiomysql` hacks for async DB. FastAPI has automatic OpenAPI and type validation. |
| Frontend framework | Next.js | Vite + React | Project constraints specify shadcn which has first-class Next.js integration. Next.js API routes useful for proxying. |
| Visualization | D3.js | Chart.js / Recharts | Project constraints require D3.js. Full control needed for zoom/pan on large datasets. |
| Python package manager | uv | Poetry / pip-tools | Project constraints specify uv. Poetry is slower; pip-tools lacks workspace support. |
| CSS framework | Tailwind | CSS Modules | shadcn/ui is built on Tailwind. CSS Modules would require component rewriting. |
## Installation
### Backend (FastAPI + uv)
# Install uv if not present
# Create project
# Add dependencies
# Run development
### Frontend (Next.js + shadcn)
# Create Next.js project
# Enter directory
# Initialize shadcn/ui
# Add components
### Dependencies (pyproject.toml)
### Dependencies (package.json)
## Docker Setup
### Backend Dockerfile
# backend/Dockerfile
# Install uv
# Install dependencies first (optimize layer caching)
# Copy application code
# Install project in editable mode
# Run with multiple workers for production
### Frontend Dockerfile
# frontend/Dockerfile
# Install dependencies only when needed
# Rebuild the source code
# Production image
### docker-compose.yml
## Reverso Integration Approach
# app/services/reverso.py
### FastAPI Endpoint Pattern
# app/main.py
## What NOT to Use and Why
| Avoid | Reason |
|-------|--------|
| **Flask** | No async support natively; would bottleneck on concurrent CSV processing |
| **pip** | Slow, no lock file; use uv as specified |
| **React class components** | shadcn/ui is designed for hooks/functional components |
| **Chart.js/Recharts** | Project constraints require D3.js for full visualization control |
| **CSS-in-JS (styled-components)** | shadcn/ui uses Tailwind; styled-components adds runtime overhead |
| **SQLite for large CSVs** | 50K+ row files should stay as pandas DataFrames; SQLite overhead unnecessary |
| **CPU-only inference** | Reverso requires CUDA GPU per project constraints |
## Sources
- FastAPI: https://fastapi.tiangolo.com (v0.128.0)
- Next.js App Router: https://nextjs.org/docs/app (v15.x)
- shadcn/ui: https://ui.shadcn.com (v0.9.x)
- D3.js zoom: https://d3js.org/d3-zoom
- uv Docker guide: https://docs.astral.sh/uv/guides/integration/docker
- uni2ts/Moirai (reference): https://github.com/SalesforceAIResearch/uni2ts
- **Reverso model: NOT FOUND** — https://github.com/SalesforceAIResearch/Reverso returned 404
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

### Python Package Management
- **Always use `uv add` instead of `pip install`** for any Python dependency command
- Run from `backend/` directory: `uv add <package>` or `uv add --dev <package>`
- Never use bare `pip install` — always prefix with `uv`
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.OpenCode/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using edit, write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-OpenCode-profile` -- do not edit manually.
<!-- GSD:profile-end -->
