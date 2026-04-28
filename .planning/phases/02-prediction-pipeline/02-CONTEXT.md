# Phase 02: Prediction Pipeline - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

End-to-end prediction pipeline: CSV file upload, parsing, configuration (context size, prediction length, frequency), and generating predictions using TimesFM2p5Model via darts.

**Scope:** Backend API endpoints, CSV processing, data normalization, async prediction job management.
**Out of scope:** Frontend UI (Phase 3), visualization, user-facing metrics display.

</domain>

<decisions>
## Implementation Decisions

### API Design for Predictions
- **D-01:** **Separate endpoints** for file upload vs raw data:
  - `POST /predict/file` — accepts multipart/form-data with CSV file + config fields
  - `POST /predict/data` — accepts JSON with raw time series array + config
- **D-02:** **Multipart form-data** for file endpoint (file + config in same request)
- **D-03:** **Response format**: Forecast array + metadata:
  ```json
  {
    "forecast": [1.2, 1.3, 1.4],
    "metadata": {
      "computation_time_ms": 245,
      "model_used": "TimesFM2p5",
      "input_points": 1024,
      "prediction_length": 96
    }
  }
  ```
- **D-04:** **Always async processing** — return job ID immediately, poll for results:
  - `POST /predict/file` → returns `{ "job_id": "uuid", "status": "processing" }`
  - `GET /predict/status/{job_id}` → poll for status
  - `GET /predict/result/{job_id}` → get results when complete

### OpenCode's Discretion
- CSV parsing library selection (pandas vs polars vs custom)
- Data normalization method (min-max vs z-score)
- Error response format (RFC 7807 Problem Details vs custom)
- Job storage (in-memory dict vs Redis vs SQLite)

### Folded Todos
(None)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Model API
- `backend/app/model_loader.py` — Current ForecastingModel class with darts/TimesFM
- `backend/app/main.py` — FastAPI app setup and lifespan

### Docker Configuration
- `backend/Dockerfile` — Multi-stage build with darts dependencies
- `docker-compose.yml` — Service orchestration

### Requirements
- `.planning/REQUIREMENTS.md` — Phase 2 requirements (UPLOAD-02 through CONFIG-05)

### No external specs — requirements fully captured in decisions above

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ForecastingModel` class: Already has `load()`, `fit()`, `predict()` methods
- FastAPI app with lifespan context manager
- Health check endpoint pattern

### Established Patterns
- Async lifespan for model loading at startup
- Logging with standard Python logging module
- JSONResponse for API responses

### Integration Points
- New prediction endpoints will connect to existing `_model` instance loaded in lifespan
- CSV processing will feed into existing `ForecastingModel.fit()` and `.predict()` methods

</code_context>

<specifics>
## Specific Ideas

- TimesFM2p5Model requires darts TimeSeries objects — need to convert CSV → pandas → TimeSeries
- CPU-only inference confirmed working in Docker
- Docker image size: ~2GB with darts + torch CPU
- User communicates in Spanish but implementation in English

</specifics>

<deferred>
## Deferred Ideas

(None — discussion stayed within phase scope)

### Reviewed Todos (not folded)
(None)

</deferred>

---

*Phase: 02-prediction-pipeline*
*Context gathered: 2026-04-28*
