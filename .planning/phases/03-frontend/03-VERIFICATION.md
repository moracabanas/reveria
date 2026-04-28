---
phase: 03-frontend
verified: 2026-04-29T01:10:00Z
status: human_needed
score: 10/10 must-haves verified
overrides_applied: 0
gaps: []
human_verification:
  - test: "Visual dashboard layout and responsiveness"
    expected: "Dashboard renders correctly at 1280px (3-column grid) and 768px (stacked vertical). Upload, config, metrics, chart, and export sections are clearly visible and well-spaced."
    why_human: "Cannot programmatically verify visual layout, spacing, and responsive behavior across breakpoints."
  - test: "D3 chart interactivity with real data"
    expected: "Upload a CSV file, wait for prediction to complete. Chart displays historical (blue) and prediction (orange) lines. Zoom and pan work smoothly without lag. Boundary dashed line visible at transition point."
    why_human: "D3 rendering and interactivity require a real browser with user interaction. Cannot verify zoom/pan performance or visual appearance programmatically."
  - test: "View mode toggle functionality"
    expected: "Clicking 'Both', 'Historical', and 'Prediction' buttons switches chart views correctly. Only relevant data series displayed in each mode."
    why_human: "Requires visual confirmation that SVG paths are rendered/hidden correctly."
  - test: "Export functionality - actual downloads"
    expected: "After prediction completes, click 'Download CSV' saves a file with headers [Index, Value, Type]. Click 'Download PNG' saves a chart image. Click 'Download SVG' saves raw SVG."
    why_human: "File download triggers require browser environment and user interaction. Cannot verify downloaded file contents programmatically in static verification."
  - test: "End-to-end prediction flow"
    expected: "With backend running, upload a CSV file through the frontend. Job is created, polling begins, and chart + metrics appear when prediction completes."
    why_human: "Requires both frontend and backend services running and communicating. Cannot verify full integration flow in isolated verification."
  - test: "Local development environment setup"
    expected: "Copy frontend/.env.example to frontend/.env.local and set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000. Frontend dev server (npm run dev) can successfully call backend API."
    why_human: "Env file setup is a manual step. Default empty BACKEND_URL works in Docker (nginx proxy) but needs explicit config for standalone local dev."
---

# Phase 3: Frontend Verification Report

**Phase Goal:** User-facing dashboard with CSV upload, visualization, metrics, and export

**Verified:** 2026-04-29T01:10:00Z

**Status:** human_needed

**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1   | User can upload CSV files via drag-and-drop or file picker | ✓ VERIFIED | `components/upload.tsx` (106 lines) implements drag-and-drop via `Dropzone` primitive with `onDragOver`, `onDrop`, `onChange` handlers. File input accepts `.csv`. File validation checks extension. |
| 2   | User sees interactive D3.js time series chart with zoom/pan for 50K+ points | ✓ VERIFIED | `lib/d3-chart.ts` (169 lines) uses `d3.zoom` with `scaleExtent([1, 50])`. Data sampling (`sampleRate = Math.ceil(length / 5000)`) limits rendered points for performance. SVG path rendering with `d3.line`. |
| 3   | User sees historical data and prediction overlaid in different colors | ✓ VERIFIED | `lib/d3-chart.ts` lines 80-101: historical stroke `#2563eb` (blue), prediction stroke `#f97316` (orange). Both paths rendered when `viewMode === "both"`. |
| 4   | User sees clear visual boundary between historical and predicted regions | ✓ VERIFIED | `lib/d3-chart.ts` lines 103-119: dashed vertical line (`stroke-dasharray="4,4"`) at `metadata.input_points` boundary when both series present. |
| 5   | User can toggle between historical only, prediction only, or both views | ✓ VERIFIED | `components/chart.tsx` lines 89-102: three buttons ("Both", "Historical", "Prediction") toggle internal `viewMode` state passed to `renderChart`. |
| 6   | User sees prediction computation time displayed | ✓ VERIFIED | `components/metrics.tsx` line 48: displays `metadata.computation_time_ms` with "ms" suffix. Test verifies `1500 ms` renders. |
| 7   | User sees MAE/MSE metrics when actual values are provided for comparison | ✓ VERIFIED | `components/metrics.tsx` lines 29-43: calculates MAE/MSE when `historical` and `prediction` arrays overlap. Conditionally renders metrics (lines 66-79). Tests verify calculation and conditional display. |
| 8   | User sees signal metadata (length, time range, frequency) | ✓ VERIFIED | `components/metrics.tsx` lines 51-65: displays `input_points`, `prediction_length`, `context_size`. Footer shows `model_used` and `frequency`. |
| 9   | User can download prediction results as CSV | ✓ VERIFIED | `lib/export-utils.ts` lines 3-28: `downloadCSV` generates CSV with headers `[Index, Value, Type]`. `components/export.tsx` line 16-18: CSV button wired to `downloadCSV`. Tests verify button click triggers download. |
| 10  | User can download chart as PNG/SVG image | ✓ VERIFIED | `lib/export-utils.ts` lines 30-83: `downloadChartAsPNG` (canvas-based) and `downloadChartAsSVG` (Blob-based) implementations. `components/export.tsx` lines 20-30: PNG/SVG buttons wired. Tests verify click triggers downloads. |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| `frontend/package.json` | Next.js + shadcn/ui dependencies | ✓ VERIFIED | Contains `next`, `react`, `typescript`, `tailwindcss`, `@base-ui/react`, `d3`. Build and test scripts present. |
| `frontend/app/page.tsx` | Main page rendering Dashboard | ✓ VERIFIED | 21 lines. Imports and renders `Dashboard` component. Responsive padding (`p-4 md:p-8`). |
| `frontend/app/layout.tsx` | Root layout with fonts and theme | ✓ VERIFIED | 33 lines. Geist fonts, shadcn theme CSS variables, dark mode support. |
| `frontend/components/upload.tsx` | Drag-and-drop upload component | ✓ VERIFIED | 106 lines. File validation, CSV parsing, progress bar, error display. Calls `uploadFile` API with config. |
| `frontend/components/chart.tsx` | Main chart component wrapping D3 | ✓ VERIFIED | 109 lines. ResizeObserver for responsive sizing. View mode toggles. Loading/error/null states. Accepts `chartRef` prop. |
| `frontend/components/dashboard.tsx` | Dashboard integrating all components | ✓ VERIFIED | 71 lines. Responsive grid layout (`lg:grid-cols-3`, `lg:grid-cols-4`). Wires upload, config, metrics, chart, export. |
| `frontend/components/metrics.tsx` | Metrics display panel | ✓ VERIFIED | 105 lines. Displays computation time, signal length, prediction length, context size. Calculates MAE/MSE on overlap. |
| `frontend/components/export.tsx` | Export buttons and logic | ✓ VERIFIED | 68 lines. CSV/PNG/SVG buttons with icons. Disabled when no data. Queries SVG from chartRef for image exports. |
| `frontend/components/config-panel.tsx` | Prediction configuration UI | ✓ VERIFIED | 110 lines. Context size, prediction length, frequency inputs. Apply/Reset buttons. Frequency dropdown with 7 options. |
| `frontend/components/ui/dropzone.tsx` | Reusable dropzone UI primitive | ✓ VERIFIED | 75 lines. Drag-over, drag-leave, drop handlers. Hidden file input with label. Visual feedback on drag state. |
| `frontend/lib/api.ts` | Backend API client | ✓ VERIFIED | 40 lines. `uploadFile`, `getJobStatus`, `getJobResult` functions. FormData construction for multipart upload. Error handling. |
| `frontend/lib/types.ts` | TypeScript types matching backend API | ✓ VERIFIED | 37 lines. `JobResponse`, `JobStatusResponse`, `JobResultResponse`, `PredictionMetadata`, `PredictionConfig`, `JobStatus`. |
| `frontend/lib/chart-types.ts` | Chart-specific TypeScript types | ✓ VERIFIED | 19 lines. `DataPoint`, `ChartData`, `ViewMode`. |
| `frontend/lib/d3-chart.ts` | D3.js chart rendering logic | ✓ VERIFIED | 169 lines. `renderChart` with zoom/pan, data sampling, axes, grid, boundary line, clip path. `clearChart` cleanup. |
| `frontend/lib/export-utils.ts` | Export helper functions | ✓ VERIFIED | 83 lines. `downloadCSV`, `downloadChartAsPNG`, `downloadChartAsSVG`. Blob/URL.createObjectURL pattern. Canvas 2x scaling for retina. |
| `frontend/hooks/useJobPolling.ts` | React hook for polling job status | ✓ VERIFIED | 80 lines. 1-second interval polling. Builds historical `DataPoint[]` from `originalData`. Builds prediction from forecast. Cleans up on unmount. |
| `frontend/app/globals.css` | Global styles and theme | ✓ VERIFIED | 155 lines. Tailwind v4 imports, shadcn theme variables, dark mode, chart container styles. |
| `frontend/next.config.ts` | Next.js configuration | ✓ VERIFIED | Static export (`output: 'export'`, `distDir: 'dist'`). TypeScript config. |

### Key Link Verification

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `upload.tsx` | `api.ts` | `import { uploadFile }` | ✓ WIRED | Line 8: import. Line 55: `uploadFile(file, config)` called in `handleUpload`. |
| `api.ts` | Backend `/predict/file` | `fetch POST` | ✓ WIRED | Line 17: `fetch(\`${BACKEND_URL}/predict/file\`, ...)`. Matches backend router at `predict.py:76`. |
| `api.ts` | Backend `/predict/status/{job_id}` | `fetch GET` | ✓ WIRED | Line 31: `fetch(\`${BACKEND_URL}/predict/status/${jobId}\`)`. Matches backend router at `predict.py:139`. |
| `api.ts` | Backend `/predict/result/{job_id}` | `fetch GET` | ✓ WIRED | Line 37: `fetch(\`${BACKEND_URL}/predict/result/${jobId}\`)`. Matches backend router at `predict.py:153`. |
| `useJobPolling.ts` | `api.ts` | `import { getJobStatus, getJobResult }` | ✓ WIRED | Lines 4-5: imports. Lines 24, 28: called in `poll()`. |
| `chart.tsx` | `d3-chart.ts` | `import { renderChart }` | ✓ WIRED | Line 6: import. Line 40: `renderChart(containerRef.current, data, options)` called in effect. |
| `dashboard.tsx` | `chart.tsx` | `import { Chart }` | ✓ WIRED | Line 5: import. Lines 58-63: `<Chart data={data} ... />` rendered. |
| `dashboard.tsx` | `upload.tsx` | `import { UploadComponent }` | ✓ WIRED | Line 4: import. Lines 41-44: `<UploadComponent onUploadComplete={...} config={config} />` rendered. Config prop passed. |
| `dashboard.tsx` | `config-panel.tsx` | `import { ConfigPanel }` | ✓ WIRED | Line 8: import. Lines 47: `<ConfigPanel config={config} onConfigChange={handleConfigChange} />` rendered. |
| `dashboard.tsx` | `metrics.tsx` | `import { MetricsPanel }` | ✓ WIRED | Line 6: import. Line 52: `<MetricsPanel data={data} />` rendered. |
| `dashboard.tsx` | `export.tsx` | `import { ExportButtons }` | ✓ WIRED | Line 7: import. Lines 66: `<ExportButtons data={data} chartRef={chartContainerRef} />` rendered. |
| `export.tsx` | `export-utils.ts` | `import { downloadCSV }` | ✓ WIRED | Line 8: import. Lines 17, 23, 29: called on button clicks. |
| `metrics.tsx` | `chart-types.ts` | `import { ChartData }` | ✓ WIRED | Line 6: import. Used in props interface and metric calculations. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `upload.tsx` | `file` | User file input | Yes — File API | ✓ FLOWING |
| `upload.tsx` | `parsedData` | `file.text()` + CSV split/parseFloat | Yes — client-side parsing | ✓ FLOWING |
| `useJobPolling.ts` | `historical` | `originalData.map()` from upload | Yes — parsed CSV values | ✓ FLOWING |
| `useJobPolling.ts` | `prediction` | `result.forecast.map()` from API | Yes — backend forecast array | ✓ FLOWING |
| `useJobPolling.ts` | `metadata` | `result.metadata` from API | Yes — backend metadata | ✓ FLOWING |
| `chart.tsx` | `data` | `useJobPolling` return | Yes — combined historical + prediction | ✓ FLOWING |
| `metrics.tsx` | `data` | `useJobPolling` return | Yes — same flow as chart | ✓ FLOWING |
| `export.tsx` | `data` | `useJobPolling` return | Yes — same flow as chart | ✓ FLOWING |
| `export.tsx` | `svg` | `chartRef.current.querySelector("svg")` | Yes — D3-rendered SVG element | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Next.js build succeeds | `cd frontend && npm run build` | Compiled successfully, static pages generated, dist/index.html created | ✓ PASS |
| Unit tests pass | `cd frontend && npm run test:run` | 4 test files, 32 tests passed, 0 failed | ✓ PASS |
| Static export produces output | `ls frontend/dist/index.html` | File exists (21KB) | ✓ PASS |
| TypeScript compilation | Build includes `Running TypeScript... Finished TypeScript` | No type errors reported | ✓ PASS |
| Test fixtures exist | `ls frontend/tests/fixtures/` | sample.csv, large_50k.csv, multi_column.csv, horno_a2_unified.csv | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| UPLOAD-01 | 03-01-PLAN.md | User can upload CSV files via drag-and-drop or file picker | ✓ SATISFIED | `components/upload.tsx` + `components/ui/dropzone.tsx` implement drag-and-drop and file picker. |
| VIZ-01 | 03-02-PLAN.md | System displays interactive D3.js time series chart | ✓ SATISFIED | `lib/d3-chart.ts` + `components/chart.tsx` render D3 SVG chart with axes, grid, lines. |
| VIZ-02 | 03-02-PLAN.md | Chart supports zoom and pan for large datasets (50K+ points) | ✓ SATISFIED | `d3.zoom` with scaleExtent [1, 50]. Data sampling every Nth point when > 5000. |
| VIZ-03 | 03-02-PLAN.md | Chart overlays historical and prediction in different colors | ✓ SATISFIED | Blue (#2563eb) historical, orange (#f97316) prediction strokes. |
| VIZ-04 | 03-02-PLAN.md | Chart shows clear visual boundary between regions | ✓ SATISFIED | Dashed vertical line at `input_points` boundary. |
| VIZ-05 | 03-02-PLAN.md | User can toggle between view modes | ✓ SATISFIED | "Both"/"Historical"/"Prediction" buttons in chart header. |
| METRICS-01 | 03-03-PLAN.md | System displays prediction computation time | ✓ SATISFIED | `metrics.tsx` displays `computation_time_ms`. |
| METRICS-02 | 03-03-PLAN.md | System shows MAE/MSE when actual values provided | ✓ SATISFIED | `metrics.tsx` calculates MAE/MSE on overlapping data. Tests verify. |
| METRICS-03 | 03-03-PLAN.md | System displays signal metadata | ✓ SATISFIED | `metrics.tsx` displays input_points, prediction_length, context_size, model_used, frequency. |
| EXPORT-01 | 03-03-PLAN.md | User can download prediction results as CSV | ✓ SATISFIED | `export-utils.ts` `downloadCSV` generates [Index, Value, Type] CSV. |
| EXPORT-02 | 03-03-PLAN.md | User can download chart as PNG/SVG image | ✓ SATISFIED | `export-utils.ts` `downloadChartAsPNG` and `downloadChartAsSVG` implementations. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `tests/chart.test.tsx` | 98 | Passes invalid `viewMode` prop to `Chart` component (component does not accept this prop) | ℹ️ Info | Test passes because React ignores unknown props, but test is slightly misleading. Does not affect production. |
| `app/layout.tsx` | 16-17 | Default Next.js metadata (`"Create Next App"`) instead of project-specific title | ℹ️ Info | Minor polish issue. Does not affect functionality. |

**No blockers or warnings found.** No TODO/FIXME comments, no empty implementations, no `console.log` in production code, no hardcoded empty data arrays flowing to rendering.

### Human Verification Required

#### 1. Visual Dashboard Layout and Responsiveness

**Test:** Open the frontend at `http://localhost:3000` in a browser. Resize window to 1280px and 768px widths.
**Expected:** Dashboard renders with upload + config side-by-side on desktop (3-column grid), stacked vertically on mobile. All cards have consistent spacing and typography.
**Why human:** Visual layout, spacing, and responsive breakpoints require a real browser viewport.

#### 2. D3 Chart Interactivity with Real Data

**Test:** Upload a CSV file (e.g., `tests/fixtures/sample.csv`) with the backend running. Wait for prediction to complete.
**Expected:** Chart appears with blue historical line and orange prediction line. Dashed vertical line at the boundary. Zoom in/out with mouse wheel and pan by dragging work smoothly.
**Why human:** D3 SVG rendering and zoom/pan behavior require a real browser with user interaction. Cannot verify 60fps performance or visual appearance programmatically.

#### 3. View Mode Toggle Functionality

**Test:** After chart renders, click "Historical", "Prediction", and "Both" buttons in sequence.
**Expected:** Chart updates to show only the selected data series. SVG paths for hidden series are removed from DOM.
**Why human:** Requires visual confirmation of SVG element visibility and correct data filtering.

#### 4. Export Functionality — Actual Downloads

**Test:** After prediction completes, click "Download CSV", "Download PNG", and "Download SVG" buttons.
**Expected:** Each button triggers a file download. CSV has correct headers and data. PNG is a valid image file. SVG is a valid SVG document.
**Why human:** Browser file download APIs (`URL.createObjectURL`, `link.click()`) require a real browser environment. Cannot verify downloaded file contents in headless verification.

#### 5. End-to-End Prediction Flow

**Test:** With backend running on `http://localhost:8000`, upload a CSV through the frontend UI.
**Expected:** Upload succeeds, job_id returned, polling begins ("Running prediction..." spinner), chart and metrics appear when job completes with status "completed".
**Why human:** Requires both frontend dev server and backend running simultaneously. Tests mock the API; real integration requires live services.

#### 6. Local Development Environment Setup

**Test:** Run `cp frontend/.env.example frontend/.env.local` and start `npm run dev` in frontend directory with backend on port 8000.
**Expected:** Frontend successfully calls backend API without CORS errors. Upload and prediction flow works end-to-end.
**Why human:** `BACKEND_URL` defaults to empty string which works in Docker (nginx proxies `/predict/` to backend) but needs explicit env var for standalone local dev. This is documented in `.env.example` but requires manual setup.

### Gaps Summary

**No implementation gaps found.** All Phase 3 roadmap success criteria and plan must-haves are satisfied in the codebase. The frontend builds successfully, all 32 unit tests pass, and all components are wired correctly.

The `human_needed` status reflects items that require visual inspection, browser interactivity, or live backend integration — all standard for frontend verification and not indicative of implementation gaps.

---

_Verified: 2026-04-29T01:10:00Z_
_Verifier: OpenCode (gsd-verifier)_
