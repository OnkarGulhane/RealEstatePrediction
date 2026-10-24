# Real Estate Price Prediction Platform — India

A modern, full-stack, machine-learning-powered web platform for estimating residential property listing prices in Indian Rupees (INR).

> **Current Repository Status: PHASES 0–7 APPROVED & VERIFIED — READY FOR PHASE 8 PRODUCTION DEPLOYMENT**  
> All core phases — Phase 0 (Architecture), Phase 1 (Data Audit), Phase 2 (Offline ML Training & Evaluation), Phase 3 (FastAPI Inference Service), Phase 4 (Django REST Framework Backend), Phase 5 (Next.js 16 Frontend), Phase 6 (Cross-Service E2E Integration), and Phase 7 (Reproducible Local Release & Dockerization) — are **100% verified and approved**.

---

## 1. Architectural Topology

The project is structured as an independently deployable monorepo with strict boundary isolation:

```text
Browser / Client (Desktop & Mobile)
                 │
                 ▼ [HTTP / JSON, Port 3000]
   ┌─────────────────────────────────────────┐
   │ Next.js 16 Ivory Luxury Frontend        │  Port: 3000
   │ (App Router, TypeScript, Responsive)    │
   └────────────────────┬────────────────────┘
                        │
                        ▼ [HTTP REST /api/v1/..., Port 8000]
   ┌─────────────────────────────────────────┐
   │ Django REST Framework Application API   │  Port: 8000
   │ (SimpleJWT Auth, CSRF Protection, DB)   │
   └────────────────────┬────────────────────┘
                        │
                        ▼ [Protected HTTP API with X-Service-Token, Port 8001]
   ┌─────────────────────────────────────────┐
   │ FastAPI Standalone Inference Service    │  Port: 8001
   │ (Loads LightGBM Pipeline, Fast Predict) │
   └────────────────────┬────────────────────┘
                        │ Reads on startup
                        ▼
   ┌─────────────────────────────────────────┐
   │ Approved Scikit-learn Pipeline Artifact │  (model_pipeline.joblib + metadata.json)
   └─────────────────────────────────────────┘

   [OFFLINE ML PIPELINE: ml/training/]
   Data Audit -> Treatment B -> Feature Engineering -> LightGBM Regression (R² = 0.8870, MAE = 12.33 Lakhs)
```

---

## 2. Directory Structure & Responsibilities

See the canonical tracked tree reference in [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) and execution runbook in [docs/RUNBOOK.md](docs/RUNBOOK.md).

| Directory | Technology | Responsibility |
|---|---|---|
| `frontend/` | Next.js 16 (Active LTS), TypeScript 5.7 | Ivory Luxury web UI, valuation calculator, user dashboard, admin analytics portal. |
| `backend/` | Python, Django 5.2 LTS, DRF, SimpleJWT | User accounts, authentication, prediction persistence, admin summaries, inference client. |
| `inference-service/` | Python, FastAPI 0.115.14, Uvicorn | Loads versioned LightGBM pipeline into memory and serves sub-second predictions. |
| `ml/training/` | Python, scikit-learn 1.9.1, LightGBM | Offline dataset auditing, Treatment B parking logic, model training, and artifact promotion. |
| `contracts/` | OpenAPI 3.0 YAML | Formal API specifications for frontend ↔ backend and backend ↔ inference. |
| `docs/` | Markdown | Comprehensive PRD, SRS, Architecture, Implementation Plan, Testing Strategy, and Runbook. |
| `scripts/` | PowerShell & Bash | Cross-platform environment setup, service launchers, and single-command test suites. |

---

## 3. Quick Start (Native Environment)

### Step 1: Automatic Setup & Demo Data Seeding
Run the automated setup script from the repository root:

* **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/setup_dev.ps1
  ```
* **macOS / Linux (Bash):**
  ```bash
  chmod +x scripts/*.sh
  ./scripts/setup_dev.sh
  ```

### Step 2: Start Services
Start each service in a separate terminal:

1. **Inference Microservice (Port 8001):**
   ```powershell
   cd inference-service
   .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8001 --reload
   ```
2. **Backend Application API (Port 8000):**
   ```powershell
   cd backend
   .\.venv\Scripts\python.exe manage.py runserver 8000
   ```
3. **Next.js Frontend (Port 3000):**
   ```powershell
   cd frontend
   npm.cmd run dev
   ```

* Web UI: `http://localhost:3000`
* Backend Health: `http://localhost:8000/api/v1/health/`
* Inference Health: `http://localhost:8001/health/live`

---

## 4. Quick Start (Docker Compose)

The entire platform is containerized with multi-stage Dockerfiles and health check orchestration:

```bash
# Start all services
docker compose up --build

# Stop all services
docker compose down

# Start with PostgreSQL database
docker compose --profile postgres up --build
```

---

## 5. Seeded Demo Accounts

| Role | Email Address | Password | Purpose |
|---|---|---|---|
| **System Admin** | `admin@realestate.local` | `AdminPassword123!` | Admin analytics, model performance monitor, system history |
| **Standard User** | `demo@realestate.local` | `DemoPassword123!` | Valuation calculator, saved prediction history |

---

## 6. Comprehensive Automated Test Suite (192 Tests)

Run all 192 tests across every service with a single command:

* **Windows:** `powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1`
* **macOS / Linux:** `./scripts/run_all_tests.sh`

```text
==================================================================
 TOTAL AUTOMATED UNIT AND INTEGRATION TESTS: 176 PASSED / 0 FAILED
 LIVE E2E CROSS-SERVICE INTEGRATION TESTS:    16 PASSED / 0 FAILED
 TOTAL AUTOMATED TESTS:                     192 PASSED (100%)
==================================================================
```

For complete step-by-step setup guides, troubleshooting, and architectural notes, consult **[docs/RUNBOOK.md](docs/RUNBOOK.md)**.
