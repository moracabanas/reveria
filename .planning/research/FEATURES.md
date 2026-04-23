# Feature Research

**Domain:** Time Series Forecasting Dashboard
**Researched:** 2026-04-23
**Confidence:** MEDIUM (Context7 verified for D3.js/FastAPI; remaining from training data)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels broken or incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| CSV file upload with drag-drop | Entry point for all data workflows | LOW | FastAPI `UploadFile` with `python-multipart`; accept `.csv` MIME type |
| Column/series selection | Users have CSVs with multiple columns, need to pick what to forecast | LOW | Auto-detect datetime index column; show column preview before upload confirms |
| Interactive time series chart | Core visualization for understanding data and results | MEDIUM | D3.js line chart with zoom/pan; `d3-zoom` behavior with `.scaleExtent([1, 10])` |
| Historical + forecast overlay | Shows input data and predicted future on same view | LOW | Single line chart with visual break or different color/style for forecast region |
| Prediction horizon configuration | Data scientists need to control how far to forecast | LOW | Numeric input for steps/hours/days ahead; validated against model max context |
| Context length configuration | Controls how much history the model sees | LOW | Slider or numeric input; affects prediction quality vs speed |
| Forecast data export | Users need to use predictions elsewhere | LOW | Download as CSV; include original + forecast columns |
| Basic error metrics (MAE/MSE) | Validate predictions against known actuals | LOW | Compute when actuals column provided; display in sidebar/panel |
| Prediction timing display | Performance benchmarking is critical for large signals | LOW | Display elapsed time in ms; show after each prediction |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable for differentiation.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Reverso foundation model** | Zero-shot forecasting at scale (50K+ points) — no training required | MEDIUM | This IS the differentiator. Competitors require model training/tuning. |
| Frequency auto-detection | Eliminates manual configuration for common cases | MEDIUM | Detect hourly/daily/weekly from timestamps; warn on ambiguous |
| Uncertainty visualization | Shows confidence bands, not just point predictions | MEDIUM | Reverso doesn't output uncertainty by default — consider bootstrapped intervals or output quantiles if model supports |
| Multi-signal comparison overlay | Compare multiple series on same chart | MEDIUM | Up to 3-5 series with distinct colors; normalize if scales differ |
| Prediction confidence indicator | Visual cue for high/low confidence regions | LOW | Color gradient or opacity on forecast line based on uncertainty |
| Signal anomaly highlighting | Flag outliers in input data that may affect forecast | MEDIUM | Simple z-score or IQR detection; highlight points > 3σ from rolling mean |
| Dataset metadata display | Show signal properties: length, frequency, range, missing % | LOW | Display before forecast; helps users validate their data |
| Batch prediction support | Process multiple CSVs sequentially | MEDIUM | Queue system with progress tracking; useful for automated workflows |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems for this specific product.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Real-time streaming predictions** | "I want live data going in and forecasts coming out" | Requires WebSocket infrastructure, streaming parsers, GPU reservation for continuous inference; contradicts batch-focused design | Batch upload with refresh button; user re-uploads updated CSV |
| **Model training/fine-tuning** | "Can't we make it more accurate for my data?" | Goes against zero-shot Reverso design; adds ML infrastructure complexity; defeats foundation model purpose | Tune prediction parameters (context length) instead |
| **Multi-user authentication** | "Let my team access it" | Adds auth infrastructure, user management, permissions; contradicts single-user local tool design | Single local instance; Docker deploy per user |
| **Cloud hosting infrastructure** | "Just host it for me" | Operational complexity, cost, maintenance burden | Docker-ready for self-hosting; documented deployment |
| **Automated column mapping AI** | "Figure out my CSV format automatically" | CSVs vary wildly; false confidence leads to wrong forecasts | Smart defaults + manual override fallback; clearly show what was detected |
| **One-click forecasting** | "Make it even simpler" | Data scientists need control; removing parameters creates confusion about what to tune | Sensible defaults with exposed controls |

## Feature Dependencies

```
[CSV Upload]
    └──requires──> [Column Selection]
                        └──requires──> [Data Validation] (ensure numeric, check timestamps)

[Prediction Config] ──enhances──> [Forecasting]
    └── context length + horizon params affect model input shape

[Forecasting] ──requires──> [Timing Display]
    └── need to measure/compute elapsed time

[Historical + Forecast Chart] ──enhances──> [Uncertainty Visualization]
    └── confidence bands extend the basic line chart

[CSV Upload] ──enhances──> [Batch Prediction]
    └── upload flow reused for batch queue

[Metrics Display] ──requires──> [Actuals Column Selection]
    └── MAE/MSE need ground truth; show only when provided

[Multi-signal Overlay] ──conflicts──> [Single Signal Focus]
    └── different complexity level; can be same phase but separate UI paths
```

### Dependency Notes

- **CSV Upload requires Column Selection:** Can't forecast without knowing which column(s) to use
- **Prediction Config enhances Forecasting:** Context/horizon are model inputs, not separate features
- **Metrics Display requires Actuals Column:** MAE/MSE only make sense when ground truth is available; hide UI when not applicable
- **Multi-signal Overlay conflicts with Single Signal Focus:** These represent different user workflows — offer as toggle, not simultaneous

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [x] **CSV Upload** — Essential entry point; no dashboard without data input
- [x] **Column Selection** — Flexible mapping for varied CSV formats
- [x] **Reverso Model Integration** — Core value; zero-shot forecasting on uploaded signals
- [x] **Interactive D3.js Chart (zoom/pan)** — Basic exploration of 50K+ points
- [x] **Historical + Forecast Visualization** — See input history and predicted future
- [x] **Prediction Config (context, horizon)** — Control forecasting behavior
- [x] **Prediction Timing** — Performance benchmarking per PROJECT.md
- [x] **Forecast Export (CSV)** — Move predictions to other tools

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **Frequency Auto-Detection** — Reduce manual config for common cases
- [ ] **Error Metrics (MAE/MSE)** — Validation when actuals available (in PROJECT.md)
- [ ] **Dataset Metadata Display** — Show signal properties before forecasting
- [ ] **Prediction Confidence Indicator** — Visual quality cue

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Uncertainty Visualization (confidence bands)** — Requires research into Reverso output format
- [ ] **Multi-signal Comparison** — Higher complexity UI; data scientist workflow enhancement
- [ ] **Signal Anomaly Highlighting** — Useful for data quality validation
- [ ] **Batch Prediction Queue** — Automated workflow for multiple files

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| CSV Upload with column selection | HIGH | LOW | P1 |
| Reverso model integration | HIGH | MEDIUM | P1 |
| Interactive D3.js chart (zoom/pan) | HIGH | MEDIUM | P1 |
| Historical + forecast overlay | HIGH | LOW | P1 |
| Prediction timing display | HIGH | LOW | P1 |
| Prediction config (context, horizon) | HIGH | LOW | P1 |
| Forecast CSV export | HIGH | LOW | P1 |
| Error metrics (MAE/MSE) | MEDIUM | LOW | P2 |
| Frequency auto-detection | MEDIUM | MEDIUM | P2 |
| Prediction confidence indicator | MEDIUM | LOW | P2 |
| Dataset metadata display | MEDIUM | LOW | P2 |
| Uncertainty visualization (bands) | MEDIUM | HIGH | P3 |
| Multi-signal comparison | MEDIUM | MEDIUM | P3 |
| Signal anomaly highlighting | MEDIUM | MEDIUM | P3 |
| Batch prediction support | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Tableau | Power BI | Grafana | Our Approach |
|---------|---------|----------|---------|--------------|
| CSV upload | ✓ (file import) | ✓ (Get Data) | ✓ (CSV plugin) | P1 — Drag-drop with flexible column mapping |
| Model type | ARIMA/ETS (built-in) | AutoML | No native (plugins) | **P1** — Reverso zero-shot (no config) |
| Interactive chart | ✓ | ✓ | ✓ | P1 — D3.js with zoom/pan per PROJECT.md |
| Prediction config | Limited (few params) | Limited | Via plugins | P1 — Context + horizon exposed directly |
| Confidence intervals | ✓ | ✓ | Limited | P3 — Future; requires uncertainty estimation |
| Multi-series overlay | ✓ | ✓ | ✓ | P3 — Future; normalize if scales differ |
| Timing/metrics | Limited | Limited | ✓ (performance) | P1 — Explicit per PROJECT.md requirements |
| Export results | ✓ | ✓ | ✓ | P1 — CSV download |

**Key differentiation:** Reverso's zero-shot capability means no training/config vs competitors' model selection + tuning workflows.

## Sources

- **Context7 (verified):** D3.js zoom/pan documentation, FastAPI file upload handling
- **Training data (LOW confidence):** Tableau forecasting features, Power BI forecasting, Grafana time series plugins
- **Project context:** `.planning/PROJECT.md` — Reverso model specs, FastAPI + shadcn stack

---
*Feature research for: Time Series Forecasting Dashboard*
*Researched: 2026-04-23*
