# Architecture Research

**Domain:** Time Series Forecasting Dashboard (FastAPI + React/shadcn + ML Model)
**Researched:** 2026-04-23
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │  CSV Upload     │  │  D3.js Chart    │  │  Controls  │ │
│  │  Component      │  │  Component      │  │  Panel     │ │
│  └────────┬────────┘  └────────▲────────┘  └────────────┘ │
│           │                    │                            │
├───────────┴────────────────────┴────────────────────────────┤
│                      API Layer (FastAPI)                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /predict endpoint                                  │   │
│  │  - UploadFile handling (CSV)                       │   │
│  │  - PredictionRequest/Response Pydantic models      │   │
│  │  - Background task for long inference              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Model Service Layer                                │   │
│  │  - Reverso model singleton (loaded at startup)      │   │
│  │  - Inference logic                                  │   │
│  │  - GPU memory management                           │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                      Model Layer                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Reverso Model (GPU)                               │   │
│  │  - Zero-shot forecasting                            │   │
│  │  - Takes normalized [0,1] sequences                │   │
│  │  - Returns predicted future points                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Frontend (React/shadcn) | UI, file handling, visualization state | Next.js or Vite + shadcn/ui components |
| CSV Upload Component | File selection, validation, FormData construction | React form with `useState` for file + progress |
| D3.js Chart Component | Time series rendering, zoom/pan, overlays | React component with `useRef` for D3绑定 |
| FastAPI API Layer | Request routing, validation, response formatting | FastAPI with Pydantic models |
| Model Service | ML model loading, inference execution, GPU management | Singleton pattern with lifespan management |
| Reverso Model | Time series forecasting | SalesforceAIResearch Reverso (CUDA required) |

## Recommended Project Structure

```
reverio/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app with lifespan
│   │   ├── config.py            # Settings (GPU, model path)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py      # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── predict.py      # /predict endpoint
│   │   └── services/
│   │       ├── __init__.py
│   │       └── reverso.py      # Reverso model wrapper
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Main dashboard page
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ui/             # shadcn components
│   │   │   ├── csv-upload.tsx
│   │   │   ├── prediction-controls.tsx
│   │   │   └── time-series-chart.tsx
│   │   ├── lib/
│   │   │   ├── api.ts          # API client functions
│   │   │   ├── utils.ts
│   │   │   └── csv-parser.ts   # Client-side CSV handling
│   │   └── hooks/
│   │       ├── usePrediction.ts
│   │       └── useChartData.ts
│   ├── package.json
│   ├── Dockerfile
│   └── next.config.js (or vite.config.ts)
│
├── docker-compose.yml
└── README.md
```

### Structure Rationale

- **backend/app/main.py:** FastAPI app with lifespan context manager for loading ML model once at startup
- **backend/app/services/reverso.py:** Model wrapper class that handles device placement, inference
- **backend/app/routers/predict.py:** Clean separation of prediction endpoint logic
- **frontend/src/components/:** Feature-based organization (upload, chart, controls)
- **frontend/src/lib/api.ts:** Centralized API calls to avoid scattered fetch logic
- **frontend/src/hooks/:** Custom hooks for prediction state and chart data management

## Architectural Patterns

### Pattern 1: Lifespan-Based Resource Management

**What:** Load ML model once at application startup, keep in memory, clean up on shutdown
**When to use:** GPU models that are expensive to load and shouldn't be reloaded per request
**Trade-offs:** Uses memory persistently; requires proper shutdown handling

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model once at startup
    app.state.reverso = ReversoModel.load("reverso-small")
    yield
    # Cleanup on shutdown
    app.state.reverso = None

app = FastAPI(lifespan=lifespan)

@app.post("/predict")
async def predict(request: PredictionRequest, app: FastAPI):
    result = await app.state.reverso.predict(request.data)
    return result
```

### Pattern 2: Pydantic Request/Response Models

**What:** Use Pydantic models to validate API input/output with clear schema
**When to use:** Any FastAPI endpoint with structured data
**Trade-offs:** Slight overhead for validation; worth it for type safety

```python
from pydantic import BaseModel
from typing import List, Optional

class PredictionRequest(BaseModel):
    data: List[float]           # Time series values (normalized 0-1)
    context_length: int = 512   # How many points to use as context
    prediction_length: int = 96  # How many points to forecast
    frequency: str = "h"        # h=hourly, d=daily, etc.

class PredictionResponse(BaseModel):
    predictions: List[float]
    context_length: int
    prediction_length: int
    inference_time_ms: float
    model_version: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
```

### Pattern 3: Form-Based File Upload with Progress

**What:** Use FastAPI's `UploadFile` with multipart/form-data for CSV uploads
**When to use:** Large file uploads that shouldn't be loaded entirely into memory
**Trade-offs:** Requires client-side FormData construction; stream processing preferred

```python
from fastapi import FastAPI, UploadFile, File

@app.post("/predict/file")
async def predict_from_file(
    file: UploadFile,
    context_length: int = Form(default=512),
    prediction_length: int = Form(default=96),
):
    # UploadFile uses spooled storage (memory then disk)
    contents = await file.read()
    # Parse CSV, extract time series...
    result = await app.state.reverso.predict_from_csv(contents)
    return result
```

### Pattern 4: React Custom Hook for Prediction State

**What:** Encapsulate prediction fetching logic in a custom hook with loading/error states
**When to use:** Any async API call from React that needs loading UI
**Trade-offs:** Creates abstraction layer; useful for reuse across components

```typescript
function usePrediction() {
  const [state, setState] = useState<PredictionState>({
    status: 'idle',
    data: null,
    error: null,
    inferenceTime: null,
  });

  const submit = async (file: File, params: PredictionParams) => {
    setState(s => ({ ...s, status: 'loading' }));
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('context_length', params.contextLength.toString());
      formData.append('prediction_length', params.predictionLength.toString());
      formData.append('frequency', params.frequency);

      const response = await fetch('/predict/file', { method: 'POST', body: formData });
      const data = await response.json();
      setState({ status: 'success', data: data.predictions, error: null, inferenceTime: data.inference_time_ms });
    } catch (error) {
      setState({ status: 'error', data: null, error: String(error), inferenceTime: null });
    }
  };

  return { state, submit };
}
```

### Pattern 5: D3.js Chart with React useRef

**What:** Use React refs to access DOM for D3 rendering, keeping React as source of truth for data
**When to use:** Complex interactive visualizations that D3 handles better than SVG libraries
**Trade-offs:** Two-way synchronization needed; D3 and React both manipulate DOM

```typescript
function TimeSeriesChart({ historical, predictions }: ChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !historical) return;
    const svg = d3.select(svgRef.current);
    // D3 rendering logic here
  }, [historical, predictions]);

  return <svg ref={svgRef} className="w-full h-64" />;
}
```

## Data Flow

### Request Flow

```
[User selects CSV file]
    ↓
[CSV Upload Component] → validates file type/size
    ↓
[User sets parameters (context_length, prediction_length, frequency)]
    ↓
[submit handler] → constructs FormData → POST /predict/file
    ↓
[FastAPI /predict/file endpoint]
    ↓ (async)
[CSV Parser Service] → extracts column, converts to float array
    ↓
[Normalization] → scales values to [0, 1]
    ↓
[Reverso Model Inference] (GPU)
    ↓
[Denormalization] → scales predictions back to original scale
    ↓
[PredictionResponse] ← { predictions, inference_time_ms, ... }
    ↓
[React state update] → triggers chart re-render
    ↓
[D3.js Chart] → renders historical + forecast overlay
```

### State Management

```
[Upload State]
    └── file, fileName, columnMapping, parsingStatus

[Prediction State]
    └── status (idle|loading|success|error)
    └── predictions, inferenceTime
    └── parameters (context_length, prediction_length, frequency)

[Chart State]
    └── historicalData, predictionData
    └── zoomLevel, panOffset
    └── comparisonData (optional MAE/MSE overlay)
```

### Key Data Flows

1. **CSV Upload Flow:** File selection → client-side validation → FormData construction → multipart POST → server-side parsing → normalized array

2. **Prediction Flow:** Request validation → model inference → response serialization → state update → chart re-render

3. **Chart Interaction Flow:** User zoom/pan → D3 event handler → local state update → re-render (debounced)

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-100 users | Single FastAPI instance, model in memory. Frontend can be static. |
| 100-1K users | Add GPU scaling, consider model batching. Redis for caching common predictions. |
| 1K-10K users | Multiple FastAPI workers with GPU access. Job queue for long predictions (Celery + Redis). |
| 10K+ users | Kubernetes with GPU nodes. Model serving layer (Triton/TensorRT). Horizontal scaling of API. |

### Scaling Priorities

1. **First bottleneck:** GPU memory - model takes 2-3GB. Batch predictions to maximize GPU utilization.

2. **Second bottleneck:** CSV parsing - 50K+ points can be slow. Stream parse, don't load entire file.

3. **Third bottleneck:** Frontend chart rendering - D3 on 50K points needs virtualization or downsampling.

## Anti-Patterns

### Anti-Pattern 1: Model Loading Per Request

**What people do:** Load the ML model inside each request handler
**Why it's wrong:** Loading a 2GB GPU model takes 5-30 seconds. Each request would be unbearably slow.
**Do this instead:** Load model once at startup via lifespan context manager, store in `app.state`

### Anti-Pattern 2: Storing Large Files in Memory

**What people do:** `contents = await file.read()` for a 50K-row CSV without limits
**Why it's wrong:** Can exhaust memory if multiple large files uploaded simultaneously
**Do this instead:** Use `UploadFile` with spooled storage (auto memory→disk), stream-parse large files

### Anti-Pattern 3: Direct DOM Manipulation in React

**What people do:** Use `document.getElementById` inside useEffect for D3
**Why it's wrong:** Breaks React's virtual DOM, causes hard-to-debug rendering issues
**Do this instead:** Use `useRef` to get the SVG element, let D3 mutate that isolated DOM node

### Anti-Pattern 4: Synchronous Model Inference in Async Endpoint

**What people do:** `result = model.predict(data)` inside `async def`
**Why it's wrong:** Blocks the event loop; FastAPI can't handle other requests during inference
**Do this instead:** Use `run_in_executor` to run sync model code in thread pool, or make model truly async

### Anti-Pattern 5: No Response Validation

**What people do:** Return raw model output directly as JSON response
**Why it's wrong:** Leaks internal implementation details, no type safety for clients
**Do this instead:** Always wrap in Pydantic response models with `response_model`

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Reverso Model | Loaded in FastAPI lifespan, called via service layer | CUDA required. Handle OOM gracefully. |
| (Future) Model Registry | Could add MLflow/W&B for version tracking | Not needed for MVP |
| (Future) Object Storage | S3/GCS for CSV storage if users need persistence | Out of scope per requirements |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend ↔ FastAPI | HTTP REST (multipart/form-data for upload, JSON for response) | Simple, well-understood |
| FastAPI ↔ Model | Direct Python call (same process) | Fast, no serialization overhead |
| CSV Parser ↔ Model Service | Python function calls | Internal module boundaries |

### API Contract

```typescript
// POST /predict/file
// Content-Type: multipart/form-data
// Request:
{
  file: File,                    // CSV file
  context_length: number,        // default 512
  prediction_length: number,     // default 96
  frequency: string,            // "h" | "d" | "w" | "m"
  column_name?: string          // optional, auto-detect if omitted
}

// Response (200):
{
  predictions: number[],         // forecasted values (denormalized)
  context_length: number,
  prediction_length: number,
  inference_time_ms: number,
  model_version: string,
  column_detected: string,       // which column was used
  row_count: number,            // how many data points processed
  y_range: [number, number],     // original data range for chart scaling
}

// Error Response (422):
{
  error: string,
  detail: string[]
}
```

## Build Order Implications

The dependencies between components suggest this build order:

```
Phase 1: Backend Core
├── Set up FastAPI project structure
├── Implement lifespan with model loading (Reverso mock first)
├── Define Pydantic schemas
└── Create /predict endpoint skeleton

Phase 2: Model Integration
├── Implement Reverso model wrapper
├── CSV parsing service
├── Normalization/denormalization
└── End-to-end inference working

Phase 3: Frontend Foundation
├── Set up Next.js/Vite with shadcn
├── Create basic layout and routing
└── Build API client lib/api.ts

Phase 4: Upload Feature
├── CSV upload component
├── Client-side file validation
├── Column mapping UI (auto + manual)
└── FormData construction and submission

Phase 5: Visualization
├── D3.js time series chart component
├── Zoom/pan interactions
├── Forecast overlay rendering
└── Metrics display (inference time)

Phase 6: Docker & Integration
├── Dockerfile for backend (with GPU support)
├── Dockerfile for frontend
├── docker-compose.yml
└── End-to-end testing
```

**Key dependency insight:** Frontend can be developed and tested with a mock API server. Backend should be verified with curl/Postman before frontend integration.

## Sources

- [FastAPI Lifespan Documentation](https://fastapi.tiangolo.com/advanced/events/) - HIGH confidence
- [FastAPI UploadFile Documentation](https://fastapi.tiangolo.com/tutorial/request-files/) - HIGH confidence
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) - HIGH confidence
- [React useEffect Data Fetching](https://react.dev/reference/react/useEffect) - HIGH confidence
- [React useRef Documentation](https://react.dev/reference/react/useRef) - HIGH confidence
- [Pydantic Models in FastAPI](https://fastapi.tiangolo.com/tutorial/body/) - HIGH confidence
- [shadcn/ui Components](https://ui.shadcn.com/) - MEDIUM confidence (documentation)

---
*Architecture research for: Reverso Time Series Forecasting Dashboard*
*Researched: 2026-04-23*
