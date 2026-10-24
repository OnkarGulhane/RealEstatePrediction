# Real Estate Price Prediction Platform — Local Release Runbook

> **Repository:** `OnkarGulhane/RealEstatePrediction`  
> **Phase:** Phase 7 — Reproducible Local Release & Runbook  
> **Status:** APPROVED & VERIFIED  
> **Target Audiences:** Software Engineers, ML Engineers, DevOps, QA Evaluators

---

## 1. System Topology & Port Allocations

The platform operates as a decoupled, 4-tier monorepo:

| Service | Technology | Port | Primary Responsibility |
|---|---|---|---|
| **Frontend UI** | Next.js 16.4.2 (App Router), TypeScript 5.7, Tailwind/Vanilla CSS | `3000` | Ivory Luxury user interface, interactive valuation form, user dashboards, admin analytics |
| **Backend API** | Django 5.2 LTS, Django REST Framework, SimpleJWT | `8000` | Authentication, CSRF protection, prediction persistence, admin endpoints, inference proxy |
| **Inference Service** | FastAPI 0.115.14, Uvicorn, Scikit-learn 1.9.1 | `8001` | Loads versioned LightGBM model into memory, transforms features, returns strictly positive INR estimates |
| **Offline ML Pipeline** | Scikit-learn, LightGBM, Pandas 2.2.3, Joblib 1.6.0 | Offline | Data audit, unit conversion, Treatment B parking logic, pipeline cross-validation, model artifact generation |

```text
Browser / Client (Desktop & Mobile)
                 │
                 ▼ [HTTP / JSON, Port 3000]
   ┌─────────────────────────────────────────┐
   │ Next.js 16 Ivory Luxury Frontend        │
   └────────────────────┬────────────────────┘
                        │
                        ▼ [HTTP REST /api/v1/..., Port 8000]
   ┌─────────────────────────────────────────┐
   │ Django REST Framework Application API   │ (SimpleJWT + CSRFCheck)
   └────────────────────┬────────────────────┘
                        │
                        ▼ [Internal HTTP Port 8001 with X-Service-Token]
   ┌─────────────────────────────────────────┐
   │ FastAPI Inference Microservice          │
   └────────────────────┬────────────────────┘
                        │ Reads on startup
                        ▼
   ┌─────────────────────────────────────────┐
   │ Scikit-learn + LightGBM Model Artifact  │ (model_pipeline.joblib + metadata.json)
   └─────────────────────────────────────────┘
```

---

## 2. Prerequisites

Verify the following runtimes are installed on your host system:

* **Node.js:** v20.x or v22.x LTS (Tested with Node.js v24.19.0 & npm v11.17.0)
* **Python:** 3.11.x – 3.13.x (Tested with Python 3.13.5 64-bit)
* **Git:** 2.40+
* **Docker & Docker Compose (Optional):** Required only if choosing containerized workflow

---

## 3. Quick Start Option A: Native Processes (Recommended for Development)

### Step 1: Automated Environment Setup & Data Seeding
Run the automated bootstrapping script from the repository root:

* **On Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/setup_dev.ps1
  ```
* **On macOS / Linux (Bash):**
  ```bash
  chmod +x scripts/*.sh
  ./scripts/setup_dev.sh
  ```

This script will automatically:
1. Verify system prerequisites (Python 3.11+, Node 20+).
2. Install Next.js frontend dependencies via `npm install`.
3. Create isolated Python virtual environments (`backend/.venv` and `inference-service/.venv`) and install pinned dependencies.
4. Align the trained model artifact into `inference-service/artifacts/`.
5. Apply all 32 Django database migrations.
6. Seed default administrator and standard user accounts with sample historical predictions.

---

### Step 2: Starting Services
Start each service in a separate terminal window:

#### Terminal 1 — Inference Microservice (Port 8001)
```powershell
# Windows
cd inference-service
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8001 --reload

# macOS / Linux
cd inference-service
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
* **Liveness Probe:** `http://localhost:8001/health/live`
* **Readiness Probe:** `http://localhost:8001/health/ready`

#### Terminal 2 — Django Application Backend (Port 8000)
```powershell
# Windows
cd backend
.\.venv\Scripts\python.exe manage.py runserver 8000

# macOS / Linux
cd backend
./.venv/bin/python manage.py runserver 8000
```
* **Backend Health Check:** `http://localhost:8000/api/v1/health/`
* **API Documentation / Root:** `http://localhost:8000/api/v1/properties/locations/`

#### Terminal 3 — Next.js Frontend (Port 3000)
```powershell
# Windows
cd frontend
npm.cmd run dev

# macOS / Linux
cd frontend
npm run dev
```
* **Frontend Web Application:** `http://localhost:3000`

---

## 4. Quick Start Option B: Multi-Container Docker Compose

If Docker is installed on your workstation, the entire platform can be brought up using Docker Compose:

```bash
# 1. Start all 3 services (Next.js, Django, FastAPI)
docker compose up --build

# 2. To stop all services
docker compose down

# 3. Optional: Run with PostgreSQL instead of SQLite
docker compose --profile postgres up --build
```

Container Health checks will automatically orchestrate startup order:
1. `realestate-inference` starts and validates model artifact readiness.
2. `realestate-backend` waits for inference health, runs database migrations, and exposes port 8000.
3. `realestate-frontend` waits for backend health, compiles standalone server, and serves on port 3000.

---

## 5. Seeded Demo Accounts & Credentials

The database comes pre-seeded with two demo accounts for immediate evaluation:

| Role | Email Address | Password | Permissions / Capabilities |
|---|---|---|---|
| **System Administrator** | `admin@realestate.local` | `AdminPassword123!` | Access to `/admin` portal, aggregate system analytics, user audit logs, system-wide valuation history |
| **Standard User** | `demo@realestate.local` | `DemoPassword123!` | Access to `/predict` calculator, personal `/dashboard`, saved valuation history across Mumbai, Bangalore, Pune, Delhi, Hyderabad |

To reset or re-seed the database at any time:
```powershell
cd backend
.\.venv\Scripts\python.exe manage.py seed_demo_data --clear
```

---

## 6. Comprehensive Automated Test Suite (192 Tests)

The repository enforces strict regression testing across all layers:

### Run All Tests with a Single Command:
* **Windows:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1
  ```
* **macOS / Linux:**
  ```bash
  ./scripts/run_all_tests.sh
  ```

### Test Breakdown by Component:

| Test Suite | Location | Command | Tests | Focus Area |
|---|---|---|---|---|
| **Frontend Suite** | `frontend/tests/` | `npm test` | **12 passed** | API client gateway, error envelope handling, currency formatters (Crores/Lakhs), date conversions |
| **Backend Suite** | `backend/tests/` | `pytest tests -q` | **46 passed** | SimpleJWT auth, CSRFCheck cookie protection, prediction persistence, admin RBAC, seed command |
| **Inference Suite** | `inference-service/tests/` | `pytest tests -q` | **43 passed** | Liveness/readiness, Treatment B parking, feature schema validation, real artifact smoke tests |
| **ML Training Suite** | `ml/training/tests/` | `pytest tests -q` | **75 passed** | 22-feature ColumnTransformer, median imputation, unknown category encoding, non-negative checks |
| **Live E2E Suite** | `scripts/` | `python scripts/run_e2e_integration_test.py` | **16 passed** | Cross-service live flow (Ports 3000 -> 8000 -> 8001), privacy isolation, CSRF token rotation |
| **Total Test Suite** | Monorepo-wide | `scripts/run_all_tests.ps1` | **192 passed** | **100% Passing (0 failures, 0 regressions)** |

---

## 7. Troubleshooting & Operational FAQs

### Q1: `npm : File ... npm.ps1 cannot be loaded because running scripts is disabled`
* **Root Cause:** Windows PowerShell Execution Policy restricts running `.ps1` wrapper scripts.
* **Solution:** Execute commands using `npm.cmd` instead of `npm`, or run PowerShell with execution policy bypass:
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/setup_dev.ps1
  ```

### Q2: Port 3000, 8000, or 8001 is already in use
* **Detection:**
  ```powershell
  netstat -ano | findstr :3000
  netstat -ano | findstr :8000
  netstat -ano | findstr :8001
  ```
* **Solution:** Kill the hanging PID or run with an alternate port:
  ```powershell
  taskkill /PID <PID> /F
  ```

### Q3: Pytest `[WinError 5] Access is denied: ... pytest-of-USERNAME`
* **Root Cause:** Windows temporary directory permissions collision.
* **Solution:** Pytest in `backend/` and `inference-service/` has been configured with `addopts = --basetemp=.pytest_tmp -p no:cacheprovider` in `pytest.ini`. Always run pytest from the respective service folder.

### Q4: CSRF 403 Forbidden on Token Refresh or Logout
* **Root Cause:** DRF is CSRF-exempt by default, but the project implements an explicit `enforce_csrf(request)` check on cookie-backed endpoints to prevent ambient cookie attacks.
* **Solution:** Ensure the client first calls `GET /api/v1/auth/csrf/` to retrieve a masked CSRF token, and sends it in the `X-CSRFToken` request header whenever presenting the `refresh_token` cookie. The Next.js API client (`frontend/src/lib/api.ts`) handles this handshake automatically.

### Q5: How to perform a clean zero-state reset?
If you want to clear all databases, temporary files, and re-initialize from scratch:
```powershell
# 1. Remove database and temporary cache
Remove-Item -Force backend/db.sqlite3
Remove-Item -Recurse -Force backend/.pytest_tmp, inference-service/.pytest_tmp

# 2. Re-apply migrations and seed data
cd backend
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo_data
```
