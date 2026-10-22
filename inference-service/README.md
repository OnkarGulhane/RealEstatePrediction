# Standalone Inference Service

## Overview
This is the independent Python HTTP service responsible for evaluating residential property features using an approved, offline-trained machine-learning model pipeline.

## Architectural Boundaries
- **No Database Access:** Does not connect to or store user, prediction, or report records.
- **No Training at Request Time:** Models are trained strictly offline. The service loads an approved `.joblib` artifact into memory at startup.
- **Framework Status:** Built using **FastAPI** as a provisional scaffold skeleton. Final framework approval remains **PROVISIONAL / REQUIRES OWNER APPROVAL** before Phase 3 implementation begins.

## Local Running
```powershell
# Inside inference-service/
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Health Endpoints
- `GET /health/live`: Process liveness check (HTTP 200).
- `GET /health/ready`: Truthful artifact readiness check (HTTP 503 if model artifact is absent or unverified).
