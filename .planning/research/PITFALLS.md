# Pitfalls Research

**Domain:** Time Series Forecasting Dashboard
**Researched:** 2026-04-23
**Confidence:** MEDIUM

## Executive Summary

Time series forecasting dashboards fail in predictable ways that differ from typical web app pitfalls. The core challenges stem from: (1) data quality issues that silently corrupt predictions, (2) visualization miscommunication of uncertainty, (3) mismatches between user expectations and model capabilities, and (4) operational issues with GPU-based inference. This research catalogs 12 critical pitfalls specific to Reverso-powered forecasting dashboards.

---

## Critical Pitfalls

### Pitfall 1: Outliers Corrupting Forecasts

**What goes wrong:**
Extreme values in the input data cause wildly inaccurate forecasts with enormous uncertainty intervals. The model fits to outliers and projects their effect indefinitely into the future.

**Why it happens:**
Foundation models like Reverso lack the robust outlier handling that statistical models (like Prophet) explicitly address. When outliers exist in the training context, the model has no mechanism to detect or discount them. Unlike Prophet which warns about this explicitly, zero-shot models accept any normalized [0,1] input and produce outputs based purely on pattern matching.

**How to avoid:**
- Implement outlier detection before sending data to the model
- Use IQR method or percentile-based filtering
- Flag potential outliers to users with explicit warnings
- Consider showing "cleaned" vs "raw" forecast comparison

**Warning signs:**
- Predictions that spike or dip sharply at the end of the context window
- Uncertainty intervals that span the entire [0,1] range
- MAE/MSE metrics that are inexplicably poor on clean test data

**Phase to address:**
Phase 2 (Data Pipeline) — outlier handling must be built into CSV processing before model input

---

### Pitfall 2: Time Series Gaps Creating False Seasonality

**What goes wrong:**
When data has regular gaps (e.g., only working hours, only weekdays, only first-of-month), the model incorrectly infers seasonality patterns for the missing periods.

**Why it happens:**
This is well-documented in Prophet: when you only have data for part of a cycle, the seasonality is "unconstrained for the remainder" and estimated poorly. The model assumes patterns exist where data doesn't exist to validate them.

**How to avoid:**
- Detect data gaps during CSV parsing
- Automatically identify the actual data frequency
- Warn users when their data has regular gaps
- Limit predictions to time windows where historical data exists
- Document the data coverage in the UI

**Warning signs:**
- CSV parsing reveals irregular intervals
- User reports "strange patterns at night" for business-hour data
- Seasonality components show high variance in gap periods

**Phase to address:**
Phase 2 (CSV Processing & Column Mapping) — gap detection is part of data validation

---

### Pitfall 3: Normalization Mismatch

**What goes wrong:**
Users upload data with values outside [0,1] (e.g., stock prices in hundreds, sensor readings in thousands), and the model produces garbage predictions because it was designed for normalized inputs.

**Why it happens:**
Reverso explicitly requires normalized [0,1] input. If users upload raw data, the model still produces outputs, but they're meaningless relative to their original scale. There's no error — just bad predictions.

**How to avoid:**
- Auto-detect data range on upload
- Automatically normalize to [0,1] before model input
- Denormalize outputs before display
- Show both normalized context and original-scale predictions
- Never silently accept out-of-range data

**Warning signs:**
- Input data min/max is far outside [0,1]
- Predictions appear "clipped" or all at one value
- Users report predictions don't match their expected scale

**Phase to address:**
Phase 2 (CSV Processing & Column Mapping) — normalization is part of data transformation pipeline

---

### Pitfall 4: Context-Prediction Length Confusion

**What goes wrong:**
Users set prediction length longer than their context data allows, producing meaningless forecasts. Or context length is too short for the model to find patterns.

**Why it happens:**
Reverso has specific requirements about context/prediction ratios. Too little context and there's nothing to base predictions on. Too much context and the model may be overwhelmed or produce extrapolation artifacts.

**How to avoid:**
- Validate context length meets minimum requirements (typically 100+ points)
- Cap prediction length at reasonable fraction of context
- Show context coverage indicator in UI
- Provide sensible defaults based on data characteristics
- Document parameter requirements in tooltips

**Warning signs:**
- Prediction length > context length
- Very short context (< 100 points) with long prediction requested
- Context length indicator shows "low confidence" zone

**Phase to address:**
Phase 3 (Prediction Configuration UI) — parameter validation at input time

---

### Pitfall 5: GPU Availability Silent Failure

**What goes wrong:**
The dashboard appears to work but silently falls back to CPU inference (if implemented) or produces errors that are hard to interpret when GPU isn't available.

**Why it happens:**
Reverso requires CUDA-compatible GPU. Without proper error handling, users get cryptic Python/CUDA errors, or worse, the system appears to work but is unbearably slow (CPU inference on large signals).

**How to avoid:**
- Check GPU availability on startup with clear messaging
- Show GPU status in the UI (connected/disconnected)
- Provide specific error messages for GPU not found
- Implement reasonable timeout for GPU operations
- Consider CPU fallback with performance warning (or explicitly not supported)

**Warning signs:**
- Prediction takes > 30 seconds for 10K points
- Logs show CPU execution rather than CUDA
- "CUDA out of memory" errors on large files

**Phase to address:**
Phase 1 (Backend Setup) — GPU detection and error handling is foundational

---

### Pitfall 6: Large File Memory Explosion

**What goes wrong:**
Users upload 100K+ point files, and the server runs out of memory during parsing, normalization, or model inference.

**Why it happens:**
50K+ points is specifically called out in requirements. But naive CSV parsing loads everything into memory, and D3.js visualization with all points can overwhelm browsers.

**How to avoid:**
- Stream-process CSV files using chunked reading
- Downsample for visualization (LTTB algorithm)
- Send only required context window to model
- Implement pagination for data tables
- Set reasonable file size limits with clear errors

**Warning signs:**
- File size > 10MB
- Memory usage spikes during file load
- Browser becomes unresponsive with large datasets

**Phase to address:**
Phase 2 (Data Pipeline) — streaming and downsampling must be designed upfront

---

### Pitfall 7: Misleading Uncertainty Visualization

**What goes wrong:**
Confidence intervals shown in the visualization are interpreted as "the true value will be within these bounds" when they actually represent model uncertainty assumptions that may not hold.

**Why it happens:**
Prophet docs explicitly warn: uncertainty intervals "assume that the future will see the same frequency and magnitude of rate changes as the past." Reverso likely has similar assumptions. Users treat visualization bands as guarantees rather than conditional projections.

**How to avoid:**
- Add explicit disclaimers about uncertainty interpretation
- Show multiple scenarios (best/worst/expected) rather than just CI bands
- Educate users that CI width reflects past volatility, not prediction accuracy
- Consider showing historical prediction error on held-out data as calibration

**Warning signs:**
- Users ask "why didn't the actual fall within the confidence bands?"
- CI bands are very narrow (model overconfident) or very wide (poor fit)
- No historical backtesting visualization available

**Phase to address:**
Phase 3 (Visualization) — uncertainty communication is a UX design problem

---

### Pitfall 8: CSV Format Hell

**What goes wrong:**
Users upload CSVs with various formats: embedded legends, multi-header rows, different date formats, mixed value types, and the parser fails silently or misidentifies columns.

**Why it happens:**
The PROJECT.md explicitly mentions "mixed signal types (financial, sensor, energy, etc.)" and "files may include data legend headers or require manual column mapping." CSV is notoriously inconsistent across domains.

**How to avoid:**
- Auto-detect common date formats (ISO, US, EU, Unix timestamp)
- Detect header rows by content analysis (non-numeric first row)
- Offer manual column mapping as fallback
- Show preview of detected structure before confirming
- Handle embedded legends by detecting and skipping legend rows
- Support common delimiters (comma, semicolon, tab)

**Warning signs:**
- Parser produces fewer columns than CSV header shows
- Date column parsed as numeric or wrong format
- Multiple non-numeric rows detected in data section

**Phase to address:**
Phase 2 (CSV Processing & Column Mapping) — robust CSV parsing is explicitly in scope

---

### Pitfall 9: Prediction-Context Visual Confusion

**What goes wrong:**
Users can't tell where the historical data ends and the prediction begins, or they can't compare actual vs predicted values clearly.

**Why it happens:**
Standard D3 time series charts don't inherently communicate the "this is historical / this is forecast" boundary. When actual values exist for comparison, they need distinct visual treatment.

**How to avoid:**
- Use distinct colors for historical vs predicted (with legend)
- Add a vertical separator line at context boundary
- Show actual values as dots/line, predictions as dashed line or band
- Use different fill patterns for confidence intervals before/after boundary
- Include timestamp labels at key points

**Warning signs:**
- Users ask "where does the prediction start?"
- Can't clearly see if prediction overshoots/undershoots actuals
- No visual distinction between data types in chart

**Phase to address:**
Phase 3 (Visualization) — this is core D3 charting work

---

### Pitfall 10: Metric Shopping

**What goes wrong:**
Users switch between MAE/MSE/RMSE looking for the "best" metric without understanding that these measure different things and all are sensitive to outliers.

**Why it happens:**
When actual values are available for comparison, multiple metrics can be shown. But users (and dashboards) often treat this as "pick the best number" rather than understanding what each metric reveals.

**How to avoid:**
- Show primary metric prominently with clear definition
- Explain metric choice in tooltip/FAQ
- Show metric breakdown by region (beginning, middle, end of prediction)
- Flag when metrics are suspiciously good/bad (possible overfitting or bug)
- Consider showing normalized metrics (MAPE, sMAPE) for scale-independence

**Warning signs:**
- MAE is very different from RMSE (indicates outliers)
- User selects metric that shows "best" results
- Metrics vary dramatically with small parameter changes

**Phase to address:**
Phase 3 (Metrics Display) — metric interpretation guidance is UX concern

---

### Pitfall 11: File Encoding Issues

**What goes wrong:**
CSVs with non-UTF8 encoding (Latin-1, Windows-1252, etc.) produce garbled text or fail to parse, especially with international characters in column headers.

**Why it happens:**
 macOS and Windows default to different encodings. Users may not realize their CSV isn't UTF-8, especially if it originates from Excel or region-specific software.

**How to avoid:**
- Detect encoding from BOM or content analysis
- Fall back to common encodings on parse failure
- Show encoding detected in file info
- Never assume UTF-8 without verification
- Handle common Latin-1 characters gracefully

**Warning signs:**
- Parsing errors on files that "look fine"
- Garbled text in column headers or values
- Encoding detection shows non-UTF8

**Phase to address:**
Phase 2 (CSV Processing) — encoding handling is part of robust file parsing

---

### Pitfall 12: "It Works in the Demo, Broken in Production"

**What goes wrong:**
Dashboard works with small demo files but fails or times out with real-world data sizes, different date ranges, or specific signal types.

**Why it happens:**
Demo data is typically clean, small, and well-behaved. Production data from users has: irregular intervals, missing values, outliers, seasonal gaps, and is 10-100x larger.

**How to avoid:**
- Test with data at the stated limits (50K+ points)
- Test with dirty data: gaps, outliers, mixed formats
- Test with diverse signal types (financial, sensor, energy)
- Test with extreme date ranges (very old, very new, leap years)
- Include stress testing in CI/CD pipeline

**Warning signs:**
- Only tested with provided demo data
- No load testing for large file handling
- No tests for data edge cases

**Phase to address:**
All phases — this is a testing discipline, but Phase 4 (Integration & Polish) should explicitly validate

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|----------------|
| Skip outlier detection | Faster MVP | Corrupted predictions, user distrust | Never |
| Load entire CSV into memory | Simpler code | OOM on large files | MVP only, must add streaming later |
| Use single color for all data | Faster D3 implementation | User confusion | Never |
| Skip GPU error handling | Faster integration | Unhelpful errors, support burden | Never |
| Hardcode date format | Simpler parsing | Fails on real CSVs | Never |
| Show only one metric | Less UI complexity | Users misinterpret results | MVP only |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Reverso Model | Sending unnormalized data | Always normalize [0,1] before inference |
| FastAPI | Not handling GPU errors gracefully | Explicit CUDA check with user message |
| D3.js | Drawing all 50K points | LTTB downsampling for performance |
| CSV parsing | Assuming UTF-8 | Encoding detection with fallback |
| File upload | No size limit | Limit to 50MB with clear error |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full CSV in memory | Server OOM, swap usage | Stream with chunked reading | Files > 20MB |
| D3 all points | Browser freezes, 60fps drop | LTTB downsampling to 5K points max | > 10K points displayed |
| GPU memory overflow | CUDA OOM crash | Batch large signals, warn on size | Signals > 100K points |
| Synchronous inference | Request timeout | Async with progress updates | Context > 20K points |
| No result caching | Repeated predictions slow | Cache by input hash + params | Same file re-uploaded |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| No file size limit | DoS via massive upload | Limit to 50MB, show clear error |
| No file type validation | Malicious file upload | Check CSV magic bytes, not just extension |
| User upload to temp directory | Path traversal | Use secure temp library, validate paths |
| No parsing timeout | CPU exhaustion | Set 30s max parse time |
| Logging raw file contents | Data leak in logs | Never log user-uploaded content |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No upload feedback | User thinks frozen | Progress bar, stage indicators |
| Cryptic parse errors | User frustration | Plain English error + fix suggestion |
| No "try sample data" | Can't test without file | Include demo dataset button |
| Parameters with no defaults | Analysis paralysis | Sensible defaults with "advanced" toggle |
| Tiny chart on large screen | Can't see details | Responsive sizing, zoom controls |
| No export of results | Can't use outputs | CSV/PNG export buttons |

---

## "Looks Done But Isn't" Checklist

- [ ] **CSV Upload:** Often missing encoding detection, large file handling, and progress feedback — verify with edge-case files
- [ ] **Normalization:** Often silently skipped — verify outputs match expected input scale
- [ ] **GPU Handling:** Often shows generic Python errors — verify clear messaging for CUDA unavailability
- [ ] **Visualization:** Often renders all points causing lag — verify smooth interaction with 50K points
- [ ] **Metrics:** Often shows numbers without context — verify explanation of what metrics mean
- [ ] **Predictions:** Often shows only yhat without uncertainty — verify CI bands visible and explained
- [ ] **File Format:** Often fails on real CSVs — verify with Excel-exported, Google Sheets-exported, and region-specific formats

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Outlier corruption | MEDIUM | Add outlier detection, re-run predictions, contact affected users |
| GPU failure | LOW | Show clear error, provide GPU troubleshooting guide |
| Memory exhaustion | MEDIUM | Kill worker, notify user, suggest smaller file |
| CSV parse failure | LOW | Offer manual column mapping, show exactly what failed |
| Wrong normalization | HIGH | Audit all predictions made, re-run with fix, document impact |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Outliers corrupting forecasts | Phase 2: Data Pipeline | Test with outlier-contaminated data |
| Time series gaps | Phase 2: CSV Processing | Test with business-hours data, weekend-only data |
| Normalization mismatch | Phase 2: Data Pipeline | Test with raw stock price data (hundreds to thousands) |
| Context-prediction confusion | Phase 3: Config UI | Test with various parameter combinations |
| GPU silent failure | Phase 1: Backend Setup | Test on machine without CUDA |
| Large file memory | Phase 2: Data Pipeline | Test with 100K point file |
| Uncertainty misinterpretation | Phase 3: Visualization | User testing with "why didn't actual fall in range?" |
| CSV format hell | Phase 2: CSV Processing | Test with 10+ different CSV formats |
| Prediction-context confusion | Phase 3: Visualization | User testing with "where does prediction start?" |
| Metric shopping | Phase 3: Metrics | User testing with metric explanation |
| File encoding | Phase 2: CSV Processing | Test with Latin-1 encoded file |
| Demo vs production gap | All phases | Explicit testing phase with edge cases |

---

## Sources

- **Prophet Outliers Documentation** — https://facebook.github.io/prophet/docs/outliers.html
- **Prophet Non-Daily Data Documentation** — https://facebook.github.io/prophet/docs/non-daily_data.html
- **Prophet Uncertainty Intervals** — https://facebook.github.io/prophet/docs/uncertainty_intervals.html
- **Pandas Time Series Documentation** — https://pandas.pydata.org/docs/user_guide/timeseries.html
- **D3 Time Module** — https://github.com/d3/d3-time
- **Reverso Model Requirements** — Per PROJECT.md: normalized [0,1] input, CUDA required, 50K+ point handling

---
*Pitfalls research for: Reverso Time Series Forecasting Dashboard*
*Researched: 2026-04-23*
