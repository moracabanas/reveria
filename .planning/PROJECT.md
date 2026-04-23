# Reverso Signal Dashboard

## What This Is

A web dashboard for uploading time series CSV signals and generating predictions using the Reverso foundation model. Users upload CSV files, configure prediction parameters (context size, prediction length, frequency), and visualize forecast results with interactive D3.js charts. Designed for data scientists and analysts working with large-scale time series data (50K+ points).

## Core Value

Upload any time series CSV and get a Reverso-powered forecast in seconds with full control over prediction parameters.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] CSV upload with flexible column mapping (auto-detect legend or manual column selection)
- [ ] Reverso model integration via FastAPI microservice
- [ ] Interactive D3.js visualization with zoom/pan and comparison overlays
- [ ] Configurable prediction parameters: context size, prediction length, frequency
- [ ] Prediction time display for performance benchmarking
- [ ] Basic metrics (MAE/MSE) when actual values are available for comparison
- [ ] Docker-ready deployment for FastAPI service and frontend

### Out of Scope

- Model training or fine-tuning — zero-shot forecasting only
- Real-time streaming predictions — batch upload only
- Multi-user authentication — single user local tool
- Cloud hosting infrastructure — Docker for local/remote deployment

## Context

**Reverso Model:**
- Time series foundation model from SalesforceAIResearch
- Hybrid architecture: long convolutions + DeltaNet layers + MLP + attention decoder
- Zero-shot forecasting capability (no training required)
- Sizes: Reverso-Nano (200K), Reverso-Small (550K), Reverso (2.6M params)
- Input: normalized [0,1] sequences, output: predicted future points
- Requires CUDA-compatible GPU for inference

**Technical Stack:**
- Frontend: shadcn (React/Next.js) with D3.js
- Backend: FastAPI microservice with uv package manager
- Deployment: Docker containers

**CSV Handling:**
- Mixed signal types (financial, sensor, energy, etc.)
- Files may include data legend headers or require manual column mapping
- Support for large files (50K+ data points)

## Constraints

- **Tech Stack**: shadcn frontend, FastAPI backend, uv for Python dependencies — as specified
- **GPU Required**: Reverso inference needs CUDA-compatible GPU — not a CPU-only tool
- **Scale**: Must handle 50K+ point signals efficiently
- **Language**: Implementation in English, user communicates in Spanish

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| D3.js for visualization | Balanced interactivity and dev complexity per user request | — Pending |
| Docker-ready architecture | FastAPI + frontend containerized for easy deployment | — Pending |
| Zero-shot only | Reverso is foundation model — no training needed | — Pending |
| Large dataset support | User works with 50K+ point signals | — Pending |
| Manual column mapping fallback | CSV formats vary — can't always auto-detect | — Pending |

---

*Last updated: 2026-04-23 after initialization*
