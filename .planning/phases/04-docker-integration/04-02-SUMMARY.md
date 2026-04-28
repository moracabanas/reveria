---
phase: "04"
plan: "02"
subsystem: "docker"
tags: ["docker", "docker-compose", "orchestration", "networking"]
dependency_graph:
  requires:
    - "04-01"
  provides:
    - "docker-compose.yml"
  affects:
    - "Backend service"
    - "Frontend service"
tech_stack:
  added:
    - "Docker internal networking"
  patterns:
    - "Service orchestration"
    - "Health check driven startup"
key_files:
  created:
    - "docker-compose.yml"
metrics:
  duration: "~30 seconds"
  completed: "2026-04-28"
decisions:
  - "Use Docker internal bridge network for service-to-service communication"
  - "Frontend depends_on backend with health check condition"
  - "Both services join reverso-network for DNS-based service discovery"
---

# Phase 04 Plan 02: Update docker-compose.yml with frontend service

## One-liner
Docker Compose orchestration with backend + frontend services on internal bridge network

## Summary

Updated docker-compose.yml to include both backend (FastAPI) and frontend (Next.js/nginx) services with proper internal networking and health check coordination.

### What was built

**docker-compose.yml** changes:

1. **Backend service** additions:
   - Internal network: `reverso-network`
   - Health check: `curl` to `/health` endpoint
   - PATH includes `.venv/bin` for uv-managed dependencies

2. **Frontend service** (new):
   - Build context: `./frontend` with `Dockerfile`
   - Ports: `3000:3000` exposed to host
   - Environment: `NEXT_PUBLIC_BACKEND_URL=http://backend:8000`
   - `depends_on` with `service_healthy` condition
   - Health check: `curl` to localhost:3000

3. **Network configuration**:
   - `reverso-network` bridge driver
   - Frontend accesses backend via Docker DNS: `http://backend:8000`

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `depends_on: condition: service_healthy` | Ensures backend ready before frontend starts |
| Internal network | Backend not directly exposed, frontend proxies |
| Bridge network driver | Standard Docker networking with DNS |

### Verification

- ✅ `docker compose up --build -d` builds both images
- ✅ Both services start and reach healthy state
- ✅ Backend accessible at localhost:8000
- ✅ Frontend accessible at localhost:3000
- ✅ Health endpoints return `{"status":"healthy"}`

### Files Modified

| File | Change |
|------|--------|
| `docker-compose.yml` | Added frontend service + network (32 lines added) |

## Deviations from Plan

None - plan executed exactly as written.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| network:internal_exposure | docker-compose.yml | Internal Docker network not exposed externally |

## Self-Check: PASSED

- ✅ docker-compose.yml includes both backend and frontend
- ✅ Both services build and start successfully
- ✅ Frontend can communicate with backend via internal DNS
- ✅ Ports 8000 and 3000 accessible from host
- ✅ Commit `5360b3b` exists in git history
