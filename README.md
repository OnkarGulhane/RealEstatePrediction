# Real Estate Price Prediction Platform — India

A modern, full-stack, machine-learning-powered web platform for estimating residential property listing prices in Indian Rupees (INR).

> **Current Repository Status: SCAFFOLD STATE — PHASE 0 PLANNING**  
> This repository contains the minimally verified architectural scaffold. Product features, live ML model training, user authentication, property prediction forms, prediction history, and administrator dashboards are planned for execution across gated development phases following formal product-owner approval.

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
  │ (FastAPI - PROVISIONAL)       │
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

| Directory | Technology | Responsibility |
|---|---|---|
| `frontend/` | Next.js 14, TypeScript | Responsive web UI, property input forms, prediction results display, user dashboard. |
| `backend/` | Python, Django REST Framework | User accounts, authentication, prediction persistence, admin summaries, and orchestration. |
| `inference-service/` | Python, FastAPI (*provisional*) | Loads versioned scikit-learn pipeline into memory and serves predictions. |
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

# Frontend Type Check & Build
cd frontend
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

## 6. What Is Not Implemented in the Scaffold (Non-Goals)

- Full user registration/login and role-based permissions (Scheduled for Phase 4).
- Production property price regression model training (Scheduled for Phase 2).
- Raw dataset cleaning and duplicate row resolution (Scheduled for Phase 1).
- Database domain models, user prediction history records, and admin reports (Scheduled for Phase 4).
- Frontend interactive form components, charts, and CSV exports (Scheduled for Phase 5).
