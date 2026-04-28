---
phase: "04"
plan: "01"
subsystem: "docker"
tags: ["docker", "frontend", "nginx", "multi-stage-build"]
dependency_graph:
  requires: []
  provides:
    - "frontend/Dockerfile"
  affects:
    - "docker-compose.yml"
tech_stack:
  added:
    - "nginx:alpine"
    - "node:20-alpine"
  patterns:
    - "Multi-stage Docker build"
    - "Static site serving with nginx"
key_files:
  created:
    - "frontend/Dockerfile"
metrics:
  duration: "~1 minute build"
  completed: "2026-04-28"
decisions:
  - "Use nginx:alpine for production runtime (minimal ~15MB image vs ~200MB with Node)"
  - "Node.js 20-alpine for build stage only"
  - "Multi-stage build separates build dependencies from runtime"
---

# Phase 04 Plan 01: Create frontend multi-stage Dockerfile

## One-liner
Multi-stage Dockerfile for Next.js frontend using nginx to serve static export

## Summary

Created a production-ready multi-stage Dockerfile for the Next.js frontend that produces a minimal image (~15MB) by using nginx:alpine to serve static files instead of carrying the Node.js runtime.

### What was built

**frontend/Dockerfile** - Two-stage build:

1. **Builder stage** (`node:20-alpine`):
   - Installs python3, make, g++ for node-gyp native modules
   - Copies package.json and package-lock.json first (layer caching)
   - Runs `npm ci --ignore-scripts` to install dependencies
   - Copies source and runs `npm run build` (Next.js static export)
   - Output: `/app/dist/` with static HTML/JS/CSS

2. **Production stage** (`nginx:alpine`):
   - Removes default nginx config
   - Copies custom nginx.conf from builder
   - Copies static export from builder's `/app/dist`
   - Exposes port 3000, starts nginx

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| nginx:alpine runtime | ~15MB vs ~200MB with Node runtime |
| node:20-alpine build | Required for Next.js 16 with App Router |
| Multi-stage build | Build tools not present in production image |
| Static export | No server-side rendering needed, pure client-side |

### Verification

- ✅ Dockerfile builds successfully
- ✅ Production image does not contain build tools
- ✅ Frontend serves on port 3000
- ✅ Static export works (HTML served correctly)

### Files Modified

| File | Change |
|------|--------|
| `frontend/Dockerfile` | Created (41 lines) |

## Deviations from Plan

None - plan executed exactly as written.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| None | frontend/Dockerfile | Static file serving only, no attack surface added |

## Self-Check: PASSED

- ✅ Dockerfile exists at correct path
- ✅ Multi-stage build implemented
- ✅ Production image minimal (~15MB)
- ✅ Commit `badb2e8` exists in git history
