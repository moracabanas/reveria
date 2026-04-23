# Requirements

## v1 Requirements

### CSV Upload

- [ ] **UPLOAD-01**: User can upload CSV files via drag-and-drop or file picker
- [ ] **UPLOAD-02**: System detects CSV structure (header row, delimiter, encoding)
- [ ] **UPLOAD-03**: User can manually select which column contains the time series values
- [ ] **UPLOAD-04**: System auto-detects data legend/header rows when present
- [ ] **UPLOAD-05**: System validates CSV format and reports errors clearly

### Prediction Configuration

- [ ] **CONFIG-01**: User can set context size (number of historical time steps to feed model)
- [ ] **CONFIG-02**: User can set prediction length (number of future steps to forecast)
- [ ] **CONFIG-03**: User can set frequency/time step size for the signal
- [ ] **CONFIG-04**: User can view current prediction configuration summary
- [ ] **CONFIG-05**: Configuration changes trigger prediction re-run

### Reverso Model Integration

- [ ] **MODEL-01**: System loads Reverso model at FastAPI startup (GPU if available, CPU fallback)
- [ ] **MODEL-02**: System handles GPU/CUDA unavailability gracefully with clear error message
- [ ] **MODEL-03**: API accepts CSV data and returns prediction within reasonable time
- [ ] **MODEL-04**: System normalizes input data to [0,1] range before prediction
- [ ] **MODEL-05**: System denormalizes prediction output back to original scale

### Visualization

- [ ] **VIZ-01**: System displays interactive D3.js time series chart
- [ ] **VIZ-02**: Chart supports zoom and pan for large datasets (50K+ points)
- [ ] **VIZ-03**: Chart overlays historical data and prediction in different colors
- [ ] **VIZ-04**: Chart shows clear visual boundary between historical and predicted regions
- [ ] **VIZ-05**: User can toggle between viewing historical only, prediction only, or both

### Metrics & Feedback

- [ ] **METRICS-01**: System displays prediction computation time (ms)
- [ ] **METRICS-02**: System shows basic metrics (MAE, MSE) when actual values are provided for comparison
- [ ] **METRICS-03**: System displays signal metadata (length, time range, frequency)

### Export

- [ ] **EXPORT-01**: User can download prediction results as CSV
- [ ] **EXPORT-02**: User can download chart as PNG/SVG image

## v2 Requirements (Deferred)

- [ ] Multi-signal overlay comparison
- [ ] Uncertainty/confidence bands visualization
- [ ] Batch queue for multiple predictions
- [ ] Anomaly detection highlighting
- [ ] Signal preprocessing controls (outlier removal, gap handling)

## Out of Scope

- **Model training or fine-tuning** — Reverso is zero-shot, no training needed
- **Real-time streaming predictions** — Batch upload only
- **Multi-user authentication** — Single user local tool
- **Cloud hosting infrastructure** — Docker for local/remote deployment only
- **Model selection** — Single model (Reverso) only

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| UPLOAD-01 to UPLOAD-05 | Phase 3 | Pending |
| CONFIG-01 to CONFIG-05 | Phase 2 | Pending |
| MODEL-01 to MODEL-05 | Phase 2 | Pending |
| VIZ-01 to VIZ-05 | Phase 4 | Pending |
| METRICS-01 to METRICS-03 | Phase 4 | Pending |
| EXPORT-01 to EXPORT-02 | Phase 4 | Pending |

---
*Last updated: 2026-04-23 after requirements definition*
