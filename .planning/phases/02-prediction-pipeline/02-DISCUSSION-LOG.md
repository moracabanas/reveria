# Phase 02: Prediction Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-28
**Phase:** 02-prediction-pipeline
**Areas discussed:** API Design for Predictions

---

## API Design for Predictions

| Option | Description | Selected |
|--------|-------------|----------|
| Single /predict | Upload CSV + config + get prediction in one call | |
| Two-step | Session-based: upload file first, then call predict with config | |
| Separate endpoints | /predict/file for file upload, /predict/data for raw array data | ✓ |

**User's choice:** Separate endpoints
**Notes:** Chose separate endpoints for flexibility — file upload for CSV, data endpoint for raw arrays

---

### Request Format

| Option | Description | Selected |
|--------|-------------|----------|
| Multipart form-data | File upload + config fields in same request | ✓ |
| JSON body with base64 CSV | Everything in JSON (no multipart, but larger payload) | |
| Query params + file | Config as URL query params, CSV as multipart file | |

**User's choice:** Multipart form-data
**Notes:** Standard approach for file uploads with additional fields

---

### Response Format

| Option | Description | Selected |
|--------|-------------|----------|
| Forecast + metadata | Array + computation time, model info, signal stats | ✓ |
| Forecast only | Just the array of predicted values | |
| Forecast + download links | Predictions + links to download results | |

**User's choice:** Forecast + metadata
**Notes:** Include computation time for performance benchmarking (METRICS-01 requirement)

---

### Processing Mode

| Option | Description | Selected |
|--------|-------------|----------|
| Synchronous | Wait for prediction to complete | |
| Async for large files | Sync for small, async for 50K+ points | |
| Always async | Return job ID immediately, poll for results | ✓ |

**User's choice:** Always async
**Notes:** Consistent UX, handles both small and large files uniformly

---

## OpenCode's Discretion

- CSV parsing library selection
- Data normalization method
- Error response format
- Job storage mechanism

## Deferred Ideas

(None)
