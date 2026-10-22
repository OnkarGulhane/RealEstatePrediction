# Real Estate Price Prediction Platform — India

A modern, full-stack, machine-learning-powered web platform for estimating residential property listing prices in Indian Rupees (INR).

> **Current Repository Status: PHASE 4 APPROVED — DJANGO REST FRAMEWORK APPLICATION BACKEND**
> Phases 0 (Architecture), 1 (Data Audit), 2 (Offline ML Training & Evaluation), 3 (FastAPI Inference Service), and 4 (Django REST Framework Backend) are completed, verified, and approved by the Product Owner. Phase 5 (Next.js Frontend) is NOT STARTED.

---

## 1. Architectural Topology

The project is structured as an independently deployable monorepo with strict boundary isolation:

```text
Browser / Client (Desktop & Mobile)
                 │
                 ▼ [HTTP / JSON]
  ┌───────────────────────────────┐
  │ Next.js + TypeScript Frontend │  Port: 3000
  │ (App Router)                  │
  └──────────────┬────────────────┘
                 │
                 ▼ [HTTP / JSON API: /api/v1/...]
  ┌───────────────────────────────┐
  │ Django REST Framework Backend │  Port: 8000
  │ (Auth, DB, Prediction History)│
  └──────────────┬────────────────┘
                 │
                 ▼ [Protected HTTP API]
  ┌───────────────────────────────┐
  │ Standalone Inference Service  │  Port: 8001
  │ (FastAPI - Approved)          │
  └──────────────┬────────────────┘
                 │ Loads on startup
                 ▼
  ┌───────────────────────────────┐
  │ Approved scikit-learn Artifact│ (model_pipeline.joblib + metadata.json)
  └───────────────────────────────┘

  [OFFLINE ONLY: ml/training/]
  Audit -> Clean -> Feature Engineer -> Train -> Evaluate -> Promote Artifact
```

---

## 2. Directory Structure & Responsibilities

See the canonical tracked tree reference in [docs/FOLDER_STRUCTURE.md](file:///e:/RealEstatePrediction/docs/FOLDER_STRUCTURE.md).

| Directory | Technology | Responsibility |
|---|---|---|
| `frontend/` | Next.js 16 (Active LTS), TypeScript | Responsive web UI, property input forms, prediction results display, user dashboard. |
| `backend/` | Python, Django 5.2 LTS, DRF, SimpleJWT | User accounts, authentication, prediction persistence, admin summaries, and orchestration. |
| `inference-service/` | Python, FastAPI (Approved) | Loads versioned scikit-learn pipeline into memory and serves predictions. |
| `ml/training/` | Python, scikit-learn, pandas | Offline dataset auditing, unit normalization, model comparison, and artifact promotion. |
| `contracts/` | OpenAPI 3.0 YAML | Formal API specifications for frontend ↔ backend and backend ↔ inference. |
| `docs/` | Markdown | Governing PRD, SRS, Architecture, Implementation Plan, and Testing specifications. |
| `scripts/` | PowerShell | Windows-friendly environment setup, service launchers, and structural checks. |

---

## 3. Prerequisites

- **Node.js:** v20.x or v24.x (Tested with Node.js v24.19.0 & npm v11.17.0)
- **Python:** 3.11+ (Tested with Python 3.13.5)
- **Operating System:** Windows 10/11 (PowerShell environment)

---

## 4. Local Quick Start & Commands

### Initial Environment Setup
Run the automated PowerShell setup script from the repository root:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_dev.ps1
```

### Running Services Locally
Start each service in a separate terminal:

#### 1. Backend (Port 8000)
```powershell
cd backend
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 8000
```
- Health endpoint: `http://localhost:8000/api/v1/health/`

#### 2. Inference Service (Port 8001)
```powershell
cd inference-service
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8001 --reload
```
- Liveness check: `http://localhost:8001/health/live`
- Readiness check: `http://localhost:8001/health/ready` (Truthfully returns HTTP 503 until an approved artifact exists)

#### 3. Frontend (Port 3000)
```powershell
cd frontend
npm run dev
```
- Web interface: `http://localhost:3000`

---

## 5. Verification & Testing
Execute the test suites for each service:

```powershell
# Structural Verification
powershell -ExecutionPolicy Bypass -File scripts/check_scaffold.ps1

# Frontend Tests, Lint, Type Check & Build
cd frontend
npm test
npm run lint
npm run typecheck
npm run build

# Backend Tests & Config Check
cd backend
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\pytest.exe

# Inference Service Tests
cd inference-service
.\.venv\Scripts\pytest.exe
```

---

## 6. Docker & Containerization Status

`compose.yaml` is provided at the repository root as an architectural deployment blueprint. Note that Compose is **not yet runnable** in Phase 0 because individual service Dockerfiles (`frontend/Dockerfile`, `backend/Dockerfile`, `inference-service/Dockerfile`) are not yet authored. Local development strictly uses native processes via `scripts/setup_dev.ps1` and `scripts/run_local.ps1`.

---

## 7. Upcoming Phases & Next Steps

- **Phase 5 (Next.js Frontend):** Responsive web UI, property input form, result display with disclaimer, authenticated prediction history dashboard, admin analytics charts.
 - **Phase 6 (Integration QA):** Cross-service end-to-end testing, error handling under latency/network failures, contract test enforcement.
 - **Phase 7 & 8 (Local Release & Deployment):** Multi-service containerization, deployment runbooks.
