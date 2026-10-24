# Real Estate Price Prediction Platform — Repository Memory & Architecture Blueprint

> **Product:** Real Estate Price Prediction Platform — India  
> **Repository:** `OnkarGulhane/RealEstatePrediction`  
> **Architecture:** Monorepo with decoupled services (Next.js Frontend, Django REST Application Backend, FastAPI Inference Microservice, Offline ML Pipeline)  
> **Last Updated:** 24 October 2026 (02:55 PM IST)  
> **Published Commit:** [`1594fe9`](https://github.com/OnkarGulhane/RealEstatePrediction/commit/1594fe9) on branch `main` (`origin/main`)  
> **Current Status:** Phases 0–7 + Hyper-Local Sub-Area Neighborhood Prediction Engine **APPROVED & VERIFIED** | Phase 8 (Online Production Deployment) **READY TO COMMENCE**

---

## 1. System Topology & Monorepo Architecture

```text
                        REAL ESTATE PREDICTION ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FRONTEND LAYER (Phase 5 - Next.js)                       │
│  - Next.js 16.4.2 App Router (SSG/SSR)           - TypeScript 5.7                      │
│  - Ivory Luxury Design System (Forest Green/Gold)- Interactive Valuation Calculator     │
│  - Cascading City -> Neighborhood Sub-Area Dropdown (81 Cities, 2,800+ Localities)    │
│  - User Auth & JWT Token Refresh Flow            - Historical Predictions Explorer     │
│  - Admin Analytics & Model Metadata Visualizer   - Responsive Mobile/Desktop Design    │
└─────────────────────────────────────────▲──────────────────────────────────────────────┘
                                          │  REST HTTP (JSON, Bearer Token, CSRF Token)
                                          │  Cookie: refresh_token (HttpOnly, SameSite=Lax)
┌─────────────────────────────────────────▼──────────────────────────────────────────────┐
│                       APPLICATION BACKEND (Phase 4 - Django 5.2 LTS)                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                              API ROUTING & APPS                                  │  │
│  │  apps.accounts     (Register, Login, CSRF, Refresh, Logout, User Profile, Seed)  │  │
│  │  apps.properties   (81 Cities & Sub-Area Catalogs: city_sub_areas.json)          │  │
│  │  apps.predictions  (Prediction Orchestrator, Sub-Area DB Migration, Inference)  │  │
│  │  apps.analytics    (Admin Summary, User Audit, Prediction Records, Reports)      │  │
│  │  apps.common       (Custom RFC 7807 Error Shapes, DRF Exception Handlers)        │  │
│  └──────────────────────────────────────▲───────────────────────────────────────────┘  │
│                                         │                                              │
│  ┌──────────────────────────────────────▼───────────────────────────────────────────┐  │
│  │                            SECURITY & MIDDLEWARE LAYER                           │  │
│  │  - Django CSRFCheck Middleware on Cookie-backed endpoints (Refresh, Logout)      │  │
│  │  - SimpleJWT In-Memory Access + Cookie Rotation & Blacklisting (WhiteNoise/CORS) │  │
│  │  - Explicit CORS/CSRF Whitelist (http://localhost:3000, http://127.0.0.1:3000)   │  │
│  │  - Python-Dotenv base loader for development environment synchronization         │  │
│  └──────────────────────────────────────▲───────────────────────────────────────────┘  │
│                                         │                                              │
│  ┌──────────────────────────────────────▼───────────────────────────────────────────┐  │
│  │                               PERSISTENCE LAYER                                  │  │
│  │  - Local: SQLite (backend/db.sqlite3) with 33 migrations (incl 0002_sub_area)     │  │
│  │  - Production: PostgreSQL strictly enforced (config.settings.production)          │  │
│  └──────────────────────────────────────┬───────────────────────────────────────────┘  │
└─────────────────────────────────────────┼──────────────────────────────────────────────┘
                                          │  Internal HTTP (Port 8001)
                                          │  Header: X-Service-Token (Bearer Authentication)
                                          │  Bounded Timeout: 3.0s | Retries: 2
┌─────────────────────────────────────────▼──────────────────────────────────────────────┐
│                    INFERENCE SERVICE (Phase 3 - FastAPI 0.115.14)                      │
│  - App Routes: /health/live, /health/ready, /api/v1/predict, /api/v1/model/metadata   │
│  - Artifact Loader: Validates metadata hash, schema compatibility, target INR unit   │
│  - Feature Adapter: Maps 23 features (incl sub_area), Treatment B parking, Floors    │
│  - Tuned Model Pipeline: HistGradientBoostingRegressor (Test R²=0.7351, MAE=25.60L) │
└─────────────────────────────────────────▲──────────────────────────────────────────────┘
                                          │  Joblib Serialized Artifact + Metadata JSON
┌─────────────────────────────────────────┴──────────────────────────────────────────────┐
│                         OFFLINE ML PIPELINE (Phase 1 & 2)                              │
│  - Clean Dataset: 187,531 raw listings, 65,255 unique supervised configs             │
│  - Sub-Area Extraction: 81 Indian cities, ~800 frequent localities (min_freq=10)       │
│  - Trained Model: HistGradientBoosting (Tuned Log-Target, R² = 0.7351, MAE = 25.60L)  │
│  - Stored Artifacts: ml/training/experiments/phase2/ + inference-service/artifacts/   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Monorepo Directory Structure

```text
RealEstatePrediction/
├── compose.yaml                  # Multi-container orchestration (Next.js, Django, FastAPI, Postgres)
├── contracts/
│   ├── application-api.yaml      # OpenAPI 3.0.3 contract for Next.js <-> Django
│   └── inference-api.yaml        # OpenAPI 3.0.3 contract for Django <-> FastAPI
├── docs/                         # Authoritative Architectural & Product Specifications
│   ├── ARCHITECTURE.md           # System design & service boundaries
│   ├── DATASET_ML_SPEC.md        # Dataset audit, cleaning rules & Treatment B
│   ├── IMPLEMENTATION_PLAN.md    # Master execution plan (Phases 0-8)
│   ├── PRD.md                    # Product requirements
│   ├── RUNBOOK.md                # Phase 7 Reproducible Local Release Runbook & FAQs
│   ├── SRS.md                    # Detailed software requirements specification
│   └── TESTING_PLAN.md           # Test strategy across all components
├── backend/                      # Django REST Application Backend (Phase 4)
│   ├── Dockerfile                # Production-ready Python 3.11 slim container definition
│   ├── entrypoint.sh             # Startup migration wrapper script
│   ├── manage.py
│   ├── requirements.txt          # Python dependencies (Django 5.2, DRF, SimpleJWT, Gunicorn)
│   ├── config/                   # Multi-environment Django settings (base, dev, prod)
│   ├── apps/
│   │   ├── accounts/             # Auth, User model, JWT rotation, CSRF token view, seed command
│   │   ├── analytics/            # Admin reports, prediction aggregates, user metrics
│   │   ├── common/               # RFC 7807 error handler, custom exceptions
│   │   ├── predictions/          # Prediction history, persistence, Inference Client
│   │   └── properties/           # Public location and amenity metadata
│   └── tests/                    # 46 backend unit, integration, and security tests
├── inference-service/            # FastAPI Microservice (Phase 3)
│   ├── Dockerfile                # Python 3.11 slim container definition
│   ├── app/                      # FastAPI routes, schemas, loader, adapter
│   ├── artifacts/                # Approved model pipeline binary & metadata JSON
│   └── tests/                    # 43 inference service unit and contract tests
├── ml/                           # Offline ML Engineering (Phase 1 & 2)
│   ├── training/                 # Pipeline scripts, audit tools, and evaluation
│   └── tests/                    # 75 ML regression & pipeline tests
├── frontend/                     # Next.js Application (Phase 5)
│   ├── Dockerfile                # Multi-stage standalone Node 20 container definition
│   ├── src/                      # App router, components, hooks, api client
│   └── tests/                    # 12 frontend unit & formatting tests
├── scripts/                      # Cross-Platform Automation & Quality Assurance
│   ├── run_all_tests.ps1         # Windows single-command runner for all 176+ unit/offline tests
│   ├── run_all_tests.sh          # Unix/macOS single-command test runner
│   ├── run_e2e_integration_test.py # Live cross-service E2E test runner (16 scenarios)
│   ├── run_local.ps1             # Windows service launcher instructions
│   ├── run_local.sh              # Unix/macOS service launcher
│   ├── setup_dev.ps1             # Windows automated setup & seed data script
│   └── setup_dev.sh              # Unix/macOS automated setup script
├── progress.md                   # Real-time progress tracker and daily status
└── repomemory.md                 # Complete repository architectural memory (this file)
```

---

## 3. Key Design Decisions & Security Controls

### 3.1 Authentication & CSRF Remediation (Phase 4 P0 Resolved)
- **Token Storage Strategy:** Access token returned in JSON body for short-lived client memory storage (5 minutes). Refresh token stored in an `HttpOnly`, `SameSite=Lax`, secure cookie (7 days).
- **CSRF Protection:** Django REST Framework disables CSRF by default (`APIView.as_view()` is `@csrf_exempt`). To prevent ambient cookie attacks on `/api/v1/auth/token/refresh/` and `/api/v1/auth/logout/`, an explicit `enforce_csrf(request)` check using Django's `CSRFCheck` middleware was implemented in `apps.accounts.views`.
- **CSRF Token Bootstrap:** `GET /api/v1/auth/csrf/` returns a masked token in `{ "csrfToken": "..." }` and sets the `csrftoken` cookie for Single Page Apps.
- **Pure JSON Non-Browser Support:** Mobile or script clients submitting refresh tokens purely via `{ "refresh": "..." }` in the JSON body without cookies are allowed without CSRF, while any request presenting a refresh cookie is strictly required to pass a valid `X-CSRFToken` header matching the cookie.
- **CORS Whitelist:** Removed wildcard origins in development. Explicitly allowed `http://localhost:3000` and `http://127.0.0.1:3000` with `CORS_ALLOW_CREDENTIALS = True`.

### 3.2 Inference Resilience & Fault Tolerance
- **Backend Inference Client:** `apps.predictions.clients.inference_client.InferenceClient` handles all HTTP communication to the FastAPI service.
- **Timeouts & Circuit Safeguards:** Requests to FastAPI enforce a strict 3.0-second connection/read timeout with up to 2 retries on connection failures.
- **Persistence Guarantees:** Prediction records are persisted to SQLite/PostgreSQL **only** upon receiving an affirmative, valid, strictly positive INR estimate from FastAPI. If inference times out or fails, a structured RFC 7807 error is returned to the user without leaving orphaned or corrupt database records.

### 3.3 Database Architecture & Isolation
- **Custom User Model:** `apps.accounts.models.User` (Email primary key, case-insensitive unique constraint, role flags for normal user vs admin).
- **Prediction Record Model:** `apps.predictions.models.Prediction` stores complete input parameters snapshot (carpet/super area, BHK, baths, parking, status), optional hyper-local `sub_area`, predicted price in INR, currency, model version, and user foreign key. Migration `0002_prediction_sub_area.py` applied.
- **Object-Level Ownership:** Non-admin users can only view or delete their own predictions (`/api/v1/predictions/`). Admins can query system-wide predictions with date range filters and aggregations (`/api/v1/analytics/predictions/`).

### 3.4 Hyper-Local Sub-Area Locality Pricing Engine (Phase 7.5 Extension)
- **High-Cardinality Resolution:** Extracted 2,800+ neighborhood variations across 81 cities from `Title` and `Society`. Implemented `OneHotEncoder(min_frequency=10, handle_unknown="ignore")` to preserve ~800 statistically robust localities while mapping long-tail variants to an infrequent bucket.
- **Model Promotion & Accuracy:** Retraining improved Test $R^2$ from 0.7104 to **0.7351** and reduced holdout MAE to **INR 25.60 Lakhs** (+59.05% improvement over baseline).
- **Backward Compatibility:** `sub_area` is optional (`nullable: true`) in all contracts (`contracts/inference-api.yaml`, `contracts/application-api.yaml`). Requests specifying only city continue to receive city-wide general predictions without regression.
- **Cascading Client Autocomplete:** Next.js UI queries `/api/v1/locations/` which provides canonical city catalogs (`backend/apps/properties/data/city_sub_areas.json`). Selecting a city instantly cascades verified neighborhood choices with responsive search.

---

## 4. Comprehensive Test Suite & Verification Matrix (194 Automated Tests)

Every component is governed by automated regression tests:

| Suite | Component | Test Count | Key Invariants Verified |
|---|---|---|---|
| **Frontend Suite** | Next.js 16 | **12 passed** | API base URL trimming, in-memory ephemeral access token, CSRF masking, RFC 7807 error envelopes, Lakhs/Crores currency formatters |
| **Backend Suite** | Django 5.2 | **47 passed** | CSRF enforcement on cookies, JWT rotation/blacklisting, user registration, property metadata, prediction persistence, sub-area persistence & serialization, admin security gates, demo seeding |
| **Inference Suite** | FastAPI | **44 passed** | Liveness/readiness probes, schema version matching, sub-area feature mapping, 23-feature schema order, Treatment B parking logic, carpet/super area conversion, invalid floor rejection, real artifact smoke tests |
| **ML Pipeline Suite** | Scikit-Learn / LightGBM | **75 passed** | 23-feature column transformer (incl sub_area), missing value median imputation, unknown category encoding, non-negative prediction output |
| **Live E2E Suite** | Python Requests | **16 passed** | Live coordination across ports 3000, 8000, 8001; auth registration, valuation pipeline with sub-areas, privacy isolation (404), RBAC guards (403), logout blacklist |
| **Contract Suite** | OpenAPI 3.0.3 | **2 validated** | Zero specification errors across both `application-api.yaml` and `inference-api.yaml` |
| **Database Suite** | Django Migrations | **33 applied** | Clean zero-state database initialization without migration graph errors (incl 0002_prediction_sub_area) |
| **Total Automated Tests** | Across Monorepo | **194 passed** | **100% Passing (0 failures, 0 regressions)** |

---

## 5. Phase 8 Roadmap (Online Production Deployment)

With Phase 7 complete and verified, the project is ready for **Phase 8: Online Production Deployment**:
1. **Frontend Hosting:** Vercel deployment connected to `origin/main` with `NEXT_PUBLIC_API_BASE_URL` pointing to production API.
2. **Backend & Inference Hosting:** Render / Railway / Fly.io container deployment with health check probes and bounded internal network communication.
3. **Managed Production Database:** Managed PostgreSQL instance (Neon / Supabase / AWS RDS) with automated backups and connection pooling.
4. **Security Hardening:** SSL/TLS HTTPS certificates, production CORS whitelist, secure cookie flags (`SameSite=None` or `Lax`, `Secure=True`), and production secret manager.
5. **Production Smoke Testing:** Live verification of user signups, real valuations, and admin audit dashboards on public domain names.
