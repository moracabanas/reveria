# Project Research Summary

**Project:** Reverso Signal Dashboard
**Domain:** Time Series Forecasting Dashboard
**Researched:** 2026-04-23
**Confidence:** MEDIUM

## Executive Summary

This is a time series forecasting dashboard that leverages Reverso, a zero-shot foundation model from SalesforceAIResearch, to generate predictions on uploaded CSV signals without requiring training or fine-tuning. The product targets data scientists who need to quickly forecast 50K+ point signals across financial, sensor, and energy domains. Experts build this with FastAPI for the async backend, Next.js with shadcn/ui for the frontend, D3.js for interactive time series visualization, and PyTorch for model inference—all containerized with Docker and NVIDIA GPU support.

The recommended approach prioritizes getting a working backend with mocked Reverso integration first, then building the frontend against that API. The core value proposition is Reverso's zero-shot capability—no training, no model selection, just upload and forecast. This differs fundamentally from competitors (Tableau, Power BI, Grafana) which require ARIMA/ETS/AutoML configuration.

**Critical risk:** The Reverso model repository at `SalesforceAIResearch/Reverso` returned a 404 during research. The model may be private, renamed, or removed. Implementation must proceed with verification milestones or fallback to the Moirai/uni2ts approach from the same organization.

## Key Findings

### Recommended Stack

FastAPI 0.128.x with Uvicorn provides async-first REST API with native `UploadFile` support for CSV handling. Next.js 15.x (App Router) with shadcn/ui 0.9.x and Tailwind CSS 4.x delivers the dashboard UI. D3.js v7 handles time series visualization with zoom/pan. PyTorch 2.x runs the Reverso model with CUDA support. The `uv` package manager replaces pip for 10-100x faster Python dependency management.

**⚠️ Model verification required:** The Reverso model at `SalesforceAIResearch/Reverso` returned 404. The Moirai/uni2ts approach is the closest reference implementation. Do NOT proceed to Phase 2 without verifying model availability.

**Core technologies:**
- **FastAPI 0.128.x:** Async REST API with automatic OpenAPI docs and `UploadFile` multipart handling
- **Next.js 15.x (App Router):** Server Components reduce client bundle; file-based routing with API routes for proxying
- **shadcn/ui 0.9.x:** Copy-paste components on Radix UI primitives + Tailwind CSS—no package lock-in
- **D3.js v7:** Full control over zoom/pan for 50K+ point time series
- **PyTorch 2.x:** Reverso and time series transformers run on CUDA
- **uv:** Python package manager—10-100x faster than pip

### Expected Features

**Must have (table stakes):**
- CSV file upload with drag-drop and column selection
- Interactive D3.js time series chart with zoom/pan
- Historical + forecast overlay on same view
- Prediction horizon and context length configuration
- Prediction timing display (benchmarking per PROJECT.md)
- Forecast data export as CSV

**Should have (competitive):**
- Reverso zero-shot forecasting (the actual differentiator)
- Frequency auto-detection to reduce manual configuration
- Prediction confidence indicator (visual cue)
- Dataset metadata display (length, frequency, range, missing %)

**Defer (v2+):**
- Uncertainty visualization (confidence bands)—requires Reverso output format research
- Multi-signal comparison overlay
- Signal anomaly highlighting
- Batch prediction queue

### Architecture Approach

The system follows a three-layer architecture: Frontend (React/shadcn with D3.js charts) → API Layer (FastAPI with Pydantic models) → Model Layer (Reverso on GPU). Key patterns include lifespan-based model loading (model singleton at startup, not per-request), Pydantic request/response validation, form-based file upload with FastAPI's `UploadFile`, custom React hooks for prediction state, and D3.js bound via `useRef` to avoid React virtual DOM conflicts.

**Major components:**
1. **Frontend (Next.js/shadcn):** CSV upload, D3.js time series chart, prediction controls panel, API client
2. **FastAPI API Layer:** `/predict` endpoint with `UploadFile` handling, Pydantic schemas, lifespan-managed model service
3. **Reverso Model Service:** Singleton model loaded at startup, inference with GPU, normalization/denormalization

### Critical Pitfalls

1. **Normalization Mismatch** — Reverso requires [0,1] normalized input. Raw data (stock prices, sensor readings) will produce garbage predictions if not normalized. Must auto-detect range and normalize before inference, denormalize outputs for display.

2. **GPU Availability Silent Failure** — System appears to work on CPU but is unbearably slow, or crashes with cryptic CUDA errors. Must check GPU on startup with clear messaging and show GPU status in UI.

3. **Outliers Corrupting Forecasts** — Foundation models lack Prophet's outlier handling. Extreme values project indefinitely into forecasts. Must implement outlier detection with user warnings before sending to model.

4. **CSV Format Hell** — CSVs from different domains have embedded legends, multi-header rows, mixed date formats, non-UTF8 encoding. Must auto-detect structure with manual override fallback.

5. **Large File Memory Explosion** — 50K+ points can overwhelm server (parsing) and browser (visualization). Must stream-parse CSVs and use LTTB downsampling for D3.js rendering.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Backend Core
**Rationale:** Foundation must be solid before model integration or frontend. GPU detection and error handling are foundational—everything else depends on knowing whether CUDA is available.

**Delivers:** FastAPI project structure with lifespan-based model loading, Pydantic schemas, `/predict` endpoint skeleton with mocked response, GPU availability check with clear error messaging.

**Addresses:** Pitfall #5 (GPU silent failure)

**Uses:** FastAPI 0.128.x, Uvicorn, Pydantic, python-multipart

**Research flag:** Standard FastAPI patterns—skip deep research, use official docs

### Phase 2: Model Integration + Data Pipeline
**Rationale:** Core value delivery. Must verify Reverso model availability before starting. Data pipeline (CSV parsing, normalization, outlier detection, encoding handling) must be robust before frontend integration.

**Delivers:** Reverso model wrapper (or Moirai fallback), CSV parsing service with column detection, normalization/denormalization pipeline, outlier detection with user warnings, `/predict/file` endpoint with full flow.

**Addresses:** Pitfalls #1 (normalization), #3 (outliers), #4 (context-prediction validation), #8 (CSV format), #11 (encoding)

**Uses:** PyTorch 2.x, pandas, numpy, CUDA

**Research flag:** ⚠️ **HIGH PRIORITY** — Verify Reverso model availability. If 404 persists, pivot to Moirai/uni2ts before completing this phase.

### Phase 3: Frontend Foundation + Upload
**Rationale:** Frontend can be developed against a mock API. This phase establishes the project structure, shadcn/ui setup, and CSV upload flow.

**Delivers:** Next.js project with shadcn/ui, basic layout and routing, `lib/api.ts` client, CSV upload component with client-side validation, column mapping UI.

**Addresses:** Feature table stakes (CSV upload, column selection)

**Uses:** Next.js 15.x, shadcn/ui 0.9.x, Tailwind CSS 4.x

**Research flag:** Standard Next.js/shadcn patterns—skip deep research, use official docs

### Phase 4: Visualization
**Rationale:** D3.js time series chart with zoom/pan is the primary user interface. Must handle 50K+ points smoothly. Depends on Phase 3 for API client and Phase 2 for response format.

**Delivers:** D3.js time series chart with `useRef` binding, zoom/pan with `d3-zoom`, historical + forecast overlay with visual boundary, prediction timing display.

**Addresses:** Pitfalls #9 (prediction-context confusion), #10 (metric display)

**Research flag:** D3.js with React—well-documented, but consider LTTB downsampling research if performance issues arise

### Phase 5: Docker & Integration
**Rationale:** End-to-end working system with GPU support in containers. Production-ready deployment configuration.

**Delivers:** Backend Dockerfile with CUDA support, frontend Dockerfile with multi-stage build, docker-compose.yml with GPU device reservation, end-to-end testing.

**Addresses:** Pitfall #12 (demo vs production gap)

**Research flag:** Standard Docker patterns—use official docs

### Phase Ordering Rationale

- **Backend before frontend:** Frontend can mock API responses; backend cannot proceed without GPU verification
- **Model integration early:** This is the core risk—if Reverso is unavailable, entire approach changes
- **Visualization late:** D3.js chart depends on knowing exact API response format; build after Phase 2 completes
- **Docker last:** Integration testing validates everything works together before containerization

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | FastAPI, Next.js, shadcn, D3.js patterns HIGH confidence. Reverso model availability LOW—404 error during research. |
| Features | MEDIUM | Table stakes well-understood. Differentiators (Reverso) depend on model availability. Anti-features clearly documented. |
| Architecture | HIGH | Standard 3-layer pattern, well-documented FastAPI lifespan/Pydantic patterns, React+D3.js integration patterns verified. |
| Pitfalls | MEDIUM | 12 pitfalls documented with Prophet references. Normalization, GPU handling, CSV parsing are common ML dashboard issues. Reverso-specific behavior unverified. |

**Overall confidence:** MEDIUM

### Gaps to Address

1. **Reverso Model Availability:** Repository returned 404. Must verify before Phase 2 begins. Fallback: Moirai/uni2ts approach with adjusted API.

2. **Reverso API Contract:** Model input/output format not documented. Must reverse-engineer or contact SalesforceAIResearch for specs before Phase 2 implementation.

3. **Uncertainty Output Format:** Pitfalls document assumes Reverso can output uncertainty quantiles. If not, confidence bands feature must be dropped from roadmap.

4. **Large Dataset Performance:** LTTB downsampling mentioned but not deeply researched. May need dedicated research if 50K point rendering is slow.

## Sources

### Primary (HIGH confidence)
- [FastAPI Official Docs](https://fastapi.tiangolo.com) — Lifespan events, UploadFile, Pydantic models
- [Next.js App Router Docs](https://nextjs.org/docs/app) — Server Components, file-based routing
- [shadcn/ui](https://ui.shadcn.com) — Component documentation
- [D3.js d3-zoom](https://d3js.org/d3-zoom) — Zoom/pan behavior

### Secondary (MEDIUM confidence)
- [uni2ts/Moirai](https://github.com/SalesforceAIResearch/uni2ts) — Reference implementation for Reverso-like models
- [Prophet Outliers Documentation](https://facebook.github.io/prophet/docs/outliers.html) — Outlier handling patterns
- [Prophet Non-Daily Data](https://facebook.github.io/prophet/docs/non-daily_data.html) — Time series gap issues
- [Docker/uv Guide](https://docs.astral.sh/uv/guides/integration/docker) — Python Docker best practices

### Tertiary (LOW confidence)
- **Reverso Model:** NOT FOUND at `https://github.com/SalesforceAIResearch/Reverso` — returned 404. Needs verification before Phase 2.
- **Reverso Output Format:** Assumed to include uncertainty quantiles. If not supported, confidence visualization must be removed from roadmap.

---
*Research completed: 2026-04-23*
*Ready for roadmap: yes — with critical flag on Reverso model verification*
