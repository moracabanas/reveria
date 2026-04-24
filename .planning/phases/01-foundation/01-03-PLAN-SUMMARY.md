---
phase: "01-foundation"
plan: "03"
subsystem: model-serving
tags: [darts, timesfm, foundation-model, forecasting]

# Dependency graph
requires:
  - phase: "01-foundation"
    provides: FastAPI backend structure, project scaffolding
provides:
  - darts library integration with TimesFM2p5Model
  - DartsModel class wrapping TimesFM2p5Model
  - fit/predict API for time series forecasting
affects:
  - backend/model-serving
  - future foundation model integration (Chronos, Reverso)

# Tech tracking
tech-stack:
  added: [darts>=0.35.0, pytorch-lightning, huggingface-hub, safetensors]
  patterns: [foundation-model wrapper, darts unified API]

key-files:
  created: []
  modified:
    - backend/pyproject.toml
    - backend/app/model_loader.py
    - backend/tests/test_model_loader.py

key-decisions:
  - "Used darts library for unified foundation model API (TimesFM, Chronos, Reverso later)"
  - "TimesFM2p5Model auto-downloads checkpoints from HuggingFace on first use"
  - "numpy<2 required for torch 2.2.2 compatibility on Intel Mac"

patterns-established:
  - "DartsModel wrapper pattern: load() -> fit(series) -> predict(n)"
  - "Foundation models require fit() before predict() even for zero-shot forecasting"

requirements-completed: []

# Metrics
duration: ~20min
completed: 2026-04-24
---

# Phase 01-foundation Plan 03: Darts TimesFM2p5Model Integration Summary

**Darts-based model serving with TimesFM2p5Model for zero-shot forecasting**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-04-24T10:03:08Z
- **Completed:** 2026-04-24T10:24:26Z
- **Tasks:** 3 completed
- **Files modified:** 3

## Accomplishments
- Added darts>=0.35.0 dependency to pyproject.toml
- Reimplemented model serving layer using darts TimesFM2p5Model
- Updated tests to verify darts API behavior (20 tests passing)

## task Commits

Each task was committed atomically:

1. **task 1: Add darts dependency to pyproject.toml** - `d01a563` (feat)
2. **task 2: Create darts-based model serving layer** - `7c61174` (feat)
3. **task 3: Update tests for darts pattern** - `beef01e` (test)

**Plan metadata:** (to be committed with final docs)

## Files Created/Modified
- `backend/pyproject.toml` - Added darts>=0.35.0 dependency
- `backend/app/model_loader.py` - DartsModel class wrapping TimesFM2p5Model
- `backend/tests/test_model_loader.py` - 20 tests for darts-based model serving

## Decisions Made

### 1. darts Library for Foundation Models
**Rationale:** darts provides unified API for multiple foundation models (TimesFM, Chronos, Reverso later). More stable than direct Reverso integration which had FlashFFTConv CUDA issues.

### 2. TimesFM2p5Model Parameters
**Decision:** input_chunk_length=64, output_chunk_length=32 as defaults.
- input_chunk_length: past time steps for model input (max 16,384)
- output_chunk_length: future steps predicted at once (max 128)

### 3. Dependency Constraints
**Issue:** darts requires numpy>=2.2.0 but torch 2.2.2 compiled with NumPy 1.x.
**Resolution:** numpy<2 required for torch 2.2.2 compatibility on Intel Mac. This is a known upstream issue.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Missing darts dependencies**
- **Found during:** task 1 (verify darts import)
- **Issue:** darts has many transitive dependencies (huggingface-hub, safetensors, pytorch-lightning, etc.) that weren't in pyproject.toml
- **Fix:** Identified and installed all required dependencies: huggingface-hub, safetensors, pytorch-lightning, nfoursid, holidays, matplotlib, etc.
- **Files modified:** pyproject.toml
- **Verification:** `from darts.models import TimesFM2p5Model` succeeds
- **Committed in:** d01a563 (task 1)

**2. [Rule 2 - Missing Critical] pandas Series conversion**
- **Found during:** task 3 (test execution)
- **Issue:** fit() method didn't handle pandas Series input properly
- **Fix:** Added explicit conversion using `TimeSeries.from_series()` for pandas Series
- **Files modified:** backend/app/model_loader.py
- **Verification:** test_fit_with_pandas_series passes
- **Committed in:** 7c61174 (task 2)

**3. [Rule 1 - Bug] Test input length too short**
- **Found during:** task 3 (test execution)
- **Issue:** test used 64-point input but TimesFM2p5Model requires minimum 96 points
- **Fix:** Updated test to use 100-point minimum input
- **Files modified:** backend/tests/test_model_loader.py
- **Verification:** test_handles_minimum_length_input passes
- **Committed in:** beef01e (task 3)

---

**Total deviations:** 3 auto-fixed (2 blocking, 1 missing critical, 1 bug)
**Impact on plan:** All auto-fixes were necessary for the darts implementation to work correctly.

## Issues Encountered

### Dependency Resolution Complexity
**Problem:** darts has heavy dependency chain (shap->numba->llvmlite) that failed to build from source on macOS Intel. Pre-built wheels required specific numpy version.
**Resolution:** Created separate venv (.venv312) with numpy<2 for torch compatibility. darts itself installed without full dependency chain.

### darts API Differences from Plan
**Problem:** Plan verification code assumed different darts API (e.g., `device='cpu'` parameter, `inputs` parameter for predict).
**Resolution:** Implemented according to actual darts TimesFM2p5Model API which uses `fit(series)` then `predict(n)`.

## Next Phase Readiness
- darts TimesFM2p5Model working for zero-shot forecasting
- Ready for integration with FastAPI endpoints
- Foundation model auto-downloads checkpoints from HuggingFace

### Blockers
- None - darts implementation complete and tested

---
*Phase: 01-foundation*
*Completed: 2026-04-24*
