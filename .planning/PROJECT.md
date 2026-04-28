# Reverso Signal Dashboard

## Current State

**v0.1** — First prototype shipped (2026-04-28)

### What's Working

- FastAPI backend with darts/TimesFM2p5Model inference
- CSV upload with auto-detection (encoding, delimiter, header)
- Async job management with status polling
- D3.js interactive chart with zoom/pan (50K+ points)
- Next.js frontend with shadcn/ui
- Docker Compose deployment (backend + frontend)
- vitest + Playwright test infrastructure

### Running

```bash
docker compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Requirements

### Validated (v0.1)

- CSV upload with flexible column mapping
- Interactive D3.js visualization with zoom/pan
- Configurable prediction parameters
- Prediction time display
- Basic metrics (MAE/MSE)
- Docker deployment

### Out of Scope

- Model training or fine-tuning — zero-shot only
- Real-time streaming — batch upload only
- Multi-user authentication — single user tool
- Cloud hosting — Docker for local/remote

---

## Architecture

- **Backend**: FastAPI + darts (TimesFM2p5Model)
- **Frontend**: Next.js 15 + shadcn/ui + D3.js
- **Container**: Docker Compose (nginx reverse proxy)
- **Tests**: vitest (unit) + Playwright (E2E)

---

## Next Milestone

See `/gsd-new-milestone` to plan v0.2

---

*Last updated: 2026-04-28*
