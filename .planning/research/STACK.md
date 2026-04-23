# Technology Stack

**Project:** Reverso Signal Dashboard
**Researched:** 2026-04-23
**Confidence:** MEDIUM (Reverso model integration details unverified — public repo not found)

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

```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
mkdir backend && cd backend
uv init --type lib

# Add dependencies
uv add "fastapi>=0.128.0" "uvicorn[standard]" python-multipart pandas numpy torch

# Run development
uv run fastapi dev app/main.py --port 8000
```

### Frontend (Next.js + shadcn)

```bash
# Create Next.js project
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Enter directory
cd frontend

# Initialize shadcn/ui
npx shadcn@latest init

# Add components
npx shadcn@latest add button card input label slider tabs toast
```

### Dependencies (pyproject.toml)

```toml
[project]
name = "reverso-dashboard"
version = "0.1.0"
dependencies = [
    "fastapi>=0.128.0",
    "uvicorn[standard]>=0.30.0",
    "python-multipart>=0.0.9",
    "pandas>=2.2.0",
    "numpy>=1.26.0",
    "torch>=2.2.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.4.0",
]
```

### Dependencies (package.json)

```json
{
  "name": "reverso-dashboard-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "d3": "^7.9.0",
    "lucide-react": "^0.400.0"
  },
  "devDependencies": {
    "@types/d3": "^7.4.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "typescript": "^5.5.0"
  }
}
```

## Docker Setup

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (optimize layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-install-project

# Copy application code
COPY . .

# Install project in editable mode
RUN uv sync --frozen --no-cache

# Run with multiple workers for production
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "80", "--workers", "4"]
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

### docker-compose.yml

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:80"
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ./backend:/app
    develop:
      watch:
        - action: sync
          path: ./backend
          target: /app
        - action: rebuild
          path: ./backend/pyproject.toml

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://backend:80
    develop:
      watch:
        - action: sync
          path: ./frontend
          target: /app
        - action: rebuild
          path: ./frontend/package.json
    depends_on:
      - backend

networks:
  default:
    name: reverso-network
```

## Reverso Integration Approach

**⚠️ Verification Required:** The Reverso model repository at `SalesforceAIResearch/Reverso` returned a 404. Verify model availability before implementation.

Based on the project context (200K-2.6M params, normalized [0,1] input, zero-shot), the integration pattern would follow the **Moirai/uni2ts** approach:

```python
# app/services/reverso.py
import torch
import numpy as np
from pathlib import Path

class ReversoModel:
    def __init__(self, model_size: str = "small"):
        # Model sizes: nano (200K), small (550K), base (2.6M)
        self.model = self._load_model(model_size)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def predict(
        self,
        signal: np.ndarray,  # Shape: (sequence_length,)
        context_length: int = 512,
        prediction_length: int = 100,
    ) -> np.ndarray:
        # Normalize to [0, 1]
        signal_min = signal.min()
        signal_max = signal.max()
        normalized = (signal - signal_min) / (signal_max - signal_max + 1e-8)

        # Prepare input tensor
        input_tensor = torch.tensor(normalized, dtype=torch.float32)
        input_tensor = input_tensor.unsqueeze(0).to(self.device)  # Add batch dim

        # Run inference (implementation depends on Reverso architecture)
        with torch.no_grad():
            output = self.model(input_tensor)

        # Denormalize output
        output = output.cpu().numpy().squeeze()
        return output * (signal_max - signal_min) + signal_min
```

### FastAPI Endpoint Pattern

```python
# app/main.py
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse

app = FastAPI(title="Reverso Signal Dashboard API")

@app.post("/predict/")
async def predict(
    file: UploadFile = File(...),
    context_length: int = 512,
    prediction_length: int = 100,
):
    # Read CSV
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    # Extract signal column (auto-detect or use first numeric column)
    signal = df.select_dtypes(include=[np.number]).iloc[:, 0].values

    # Run prediction
    model = ReversoModel()
    forecast = model.predict(signal, context_length, prediction_length)

    return JSONResponse({
        "forecast": forecast.tolist(),
        "context_length": context_length,
        "prediction_length": prediction_length,
    })
```

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
