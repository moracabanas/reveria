# Roadmap

## Phases

- [x] **Phase 1: Foundation** - FastAPI project, darts TimesFM model serving (Complete ✓)
- [ ] **Phase 2: Prediction Pipeline** - CSV parsing, TimesFM inference, configuration
- [ ] **Phase 3: Frontend** - Upload UI, visualization, metrics, export
- [ ] **Phase 4: Docker & Integration** - Containerized deployment with GPU support

## Phase Details

### Phase 1: Foundation

**Goal**: FastAPI project with model loading infrastructure (CPU mode)

**Depends on**: Nothing (first phase)

**Requirements**: MODEL-01, MODEL-02

**Success Criteria** (what must be TRUE):
1. FastAPI application starts without errors
2. System loads TimesFM model at startup on CPU (via darts)
3. API responds to health check endpoint

**Plans**: 3/3 complete ✓

**Status**: Complete ✓

Plans:
- [x] 01-01-PLAN.md — Project scaffolding, model loading infrastructure
- [x] 01-02-PLAN.md — Unit tests for model loader and health endpoint
- [x] 01-03-PLAN.md — Reimplement model serving using darts library (TimesFM)

**UI hint**: no

---

### Phase 01.1: Switch to darts TimesFM (INSERTED)

**Goal:** [Urgent work - to be planned]
**Requirements**: TBD
**Depends on:** Phase 1
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd-plan-phase 01.1 to break down)

### Phase 2: Prediction Pipeline

**Goal**: End-to-end prediction pipeline with CSV handling, Reverso inference, and configuration

**Depends on**: Phase 1

**Requirements**: UPLOAD-02, UPLOAD-03, UPLOAD-04, UPLOAD-05, MODEL-03, MODEL-04, MODEL-05, CONFIG-01, CONFIG-02, CONFIG-03, CONFIG-04, CONFIG-05

**Success Criteria** (what must be TRUE):
1. User can upload CSV and system correctly detects header row, delimiter, and encoding
2. User can manually select which column contains time series values
3. System auto-detects data legend/header rows when present
4. System validates CSV format and reports errors clearly
5. System normalizes input data to [0,1] range before prediction
6. System returns prediction and denormalizes output to original scale
7. User can configure context size, prediction length, and frequency
8. User sees current prediction configuration summary
9. Configuration changes trigger prediction re-run automatically

**Plans**: TBD

**UI hint**: no

---

### Phase 3: Frontend

**Goal**: User-facing dashboard with CSV upload, visualization, metrics, and export

**Depends on**: Phase 2

**Requirements**: UPLOAD-01, VIZ-01, VIZ-02, VIZ-03, VIZ-04, VIZ-05, METRICS-01, METRICS-02, METRICS-03, EXPORT-01, EXPORT-02

**Success Criteria** (what must be TRUE):
1. User can upload CSV files via drag-and-drop or file picker
2. User sees interactive D3.js time series chart with zoom/pan for 50K+ points
3. User sees historical data and prediction overlaid in different colors
4. User sees clear visual boundary between historical and predicted regions
5. User can toggle between historical only, prediction only, or both views
6. User sees prediction computation time displayed
7. User sees MAE/MSE metrics when actual values are provided for comparison
8. User sees signal metadata (length, time range, frequency)
9. User can download prediction results as CSV
10. User can download chart as PNG/SVG image

**Plans**: TBD

**UI hint**: yes

---

### Phase 4: Docker & Integration

**Goal**: Containerized deployment and end-to-end validation

**Depends on**: Phase 3

**Requirements**: Implicit (deployment infrastructure)

**Success Criteria** (what must be TRUE):
1. Backend runs in Docker container
2. Frontend runs in Docker container with multi-stage build
3. docker-compose.yml orchestrates services
4. End-to-end prediction flow works from within containers

**Plans**: TBD

**UI hint**: no

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 3/3 | Complete | 2026-04-24 |
| 2. Prediction Pipeline | 0/9 | Not started | - |
| 3. Frontend | 0/10 | Not started | - |
| 4. Docker & Integration | 0/4 | Not started | - |

---

*Created: 2026-04-23*
