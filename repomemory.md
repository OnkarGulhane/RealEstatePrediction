# Real Estate Price Prediction Platform — Repository Memory & Architecture Blueprint

> **Product:** Real Estate Price Prediction Platform — India  
> **Repository:** `OnkarGulhane/RealEstatePrediction`  
> **Architecture:** Monorepo with decoupled services (Next.js Frontend, Django REST Application Backend, FastAPI Inference Microservice, Offline ML Pipeline)  
> **Last Updated:** 23 October 2026 (02:45 AM IST)  
> **Published Commit:** [`2b14176`](https://github.com/OnkarGulhane/RealEstatePrediction/commit/2b141766429e041b1b8d1eefbb5562f878dfffa1) on branch `main` (`origin/main`)  
> **Current Status:** Phases 0–6 **APPROVED & VERIFIED** | Phase 7 (Reproducible Local Release & Runbook) **NEXT IN LINE**

---

## 1. System Topology & Monorepo Architecture

```
                        REAL ESTATE PREDICTION ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FRONTEND LAYER (Phase 5 - Next.js)                       │
│  - Next.js 16.x App Router (SSG/SSR)             - TypeScript 5.x                      │
│  - Tailwind CSS / Vanilla CSS Design System      - Interactive Valuation Calculator     │
│  - User Auth & JWT Token Refresh Flow             - Historical Predictions Explorer    │
│  - Admin Analytics & Model Metadata Visualizer   - Responsive Mobile/Desktop Design    │
└─────────────────────────────────────────▲──────────────────────────────────────────────┘
                                          │  REST HTTP (JSON, Bearer Token, CSRF Token)
                                          │  Cookie: refresh_token (HttpOnly, SameSite=Lax)
┌─────────────────────────────────────────▼──────────────────────────────────────────────┐
│                       APPLICATION BACKEND (Phase 4 - Django 5.2 LTS)                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                              API ROUTING & APPS                                  │  │
│  │  apps.accounts     (Register, Login, CSRF, Refresh, Logout, User Profile)        │  │
│  │  apps.properties   (Supported Locations Metadata, City Catalog)                  │  │
│  │  apps.predictions  (Prediction Orchestrator, Inference HTTP Client, History)     │  │
│  │  apps.analytics    (Admin Summary, User Audit, Prediction Records, Reports)      │  │
│  │  apps.common       (Custom RFC 7807 Error Shapes, DRF Exception Handlers)        │  │
│  └──────────────────────────────────────▲───────────────────────────────────────────┘  │
│                                         │                                              │
│  ┌──────────────────────────────────────▼───────────────────────────────────────────┐  │
│  │                            SECURITY & MIDDLEWARE LAYER                           │  │
│  │  - Django CSRFCheck Middleware on Cookie-backed endpoints (Refresh, Logout)      │  │
│  │  - SimpleJWT In-Memory Access + Cookie Rotation & Blacklisting (WhiteNoise/CORS) │  │
│  │  - Explicit CORS/CSRF Whitelist (http://localhost:3000, http://127.0.0.1:3000)   │  │
│  └──────────────────────────────────────▲───────────────────────────────────────────┘  │
│                                         │                                              │
│  ┌──────────────────────────────────────▼───────────────────────────────────────────┐  │
│  │                               PERSISTENCE LAYER                                  │  │
│  │  - Local: SQLite (backend/db.sqlite3) with 32 migrations                         │  │
│  │  - Production: PostgreSQL strictly enforced (config.settings.production)          │  │
│  └──────────────────────────────────────┬───────────────────────────────────────────┘  │
└─────────────────────────────────────────┼──────────────────────────────────────────────┘
                                          │  Internal HTTP (Port 8001)
                                          │  Header: X-Service-Token (Bearer Authentication)
                                          │  Bounded Timeout: 3.0s | Retries: 2
┌─────────────────────────────────────────▼──────────────────────────────────────────────┐
│                    INFERENCE SERVICE (Phase 3 - FastAPI 0.115.14)                      │
│  - App Routes: /health/live, /health/ready, /predict, /metadata/model                  │
│  - Artifact Loader: Validates metadata hash, schema compatibility, target INR unit   │
│  - Feature Adapter: Transforms Carpet/Super Area, Treatment B parking, Floor mapping    │
│  - LightGBM Pipeline: 22 engineered features, strictly positive INR output checks     │
└─────────────────────────────────────────▲──────────────────────────────────────────────┘
                                          │  Joblib Serialized Artifact + Metadata JSON
┌─────────────────────────────────────────┴──────────────────────────────────────────────┐
│                         OFFLINE ML PIPELINE (Phase 1 & 2)                              │
│  - Clean Dataset: 177,847 continuous INR asking price rows, 65,255 unique configs     │
│  - Treatment B: Raw 21-50 parking spaces preserved, missing median imputed             │
│  - Trained Model: LightGBM Regressor (R² = 0.8870, MAE = 12.33 Lakhs INR)              │
│  - Stored Artifacts: ml/artifacts/final_model.joblib + metadata.json                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Monorepo Directory Structure

```
RealEstatePrediction/
├── contracts/
│   ├── application-api.yaml      # OpenAPI 3.0.3 contract for Next.js <-> Django
│   └── inference-api.yaml        # OpenAPI 3.0.3 contract for Django <-> FastAPI
├── docs/                         # Authoritative Architectural & Product Specifications
│   ├── ARCHITECTURE.md           # System design & service boundaries
│   ├── DATASET_ML_SPEC.md        # Dataset audit, cleaning rules & Treatment B
│   ├── IMPLEMENTATION_PLAN.md    # Master execution plan (Phases 0-8)
│   ├── PRD.md                    # Product requirements
│   ├── SRS.md                    # Detailed software requirements specification
│   └── TESTING_PLAN.md           # Test strategy across all components
├── backend/                      # Django REST Application Backend (Phase 4)
│   ├── manage.py
│   ├── requirements.txt          # Python dependencies (Django 5.2, DRF, SimpleJWT, etc.)
│   ├── config/                   # Multi-environment Django settings (base, dev, prod)
│   ├── apps/
│   │   ├── accounts/             # Auth, User model, JWT rotation, CSRF token view
│   │   ├── analytics/            # Admin reports, prediction aggregates, user metrics
│   │   ├── common/               # RFC 7807 error handler, custom exceptions
│   │   ├── predictions/          # Prediction history, persistence, Inference Client
│   │   └── properties/           # Public location and amenity metadata
│   └── tests/                    # 45 backend unit, integration, and security tests
├── inference-service/            # FastAPI Microservice (Phase 3)
│   ├── app/                      # FastAPI routes, schemas, loader, adapter
│   └── tests/                    # 43 inference service unit and contract tests
├── ml/                           # Offline ML Engineering (Phase 1 & 2)
│   ├── artifacts/                # Trained LightGBM model binary & metadata JSON
│   ├── training/                 # Pipeline scripts, audit tools, and evaluation
│   └── tests/                    # 75 ML regression & pipeline tests
├── frontend/                     # Next.js Application (Phase 5 - Starting Tomorrow)
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
- **Custom User Model:** `apps.accounts.models.User` (UUID primary key, case-insensitive email unique constraint, role flags for normal user vs admin).
- **Prediction Record Model:** `apps.predictions.models.PredictionRecord` stores complete input parameters snapshot (carpet/super area, BHK, baths, parking, status), predicted price in INR, price per sqft, latency in ms, model version, and user foreign key.
- **Object-Level Ownership:** Non-admin users can only view or delete their own predictions (`/api/v1/predictions/history/`). Admins can query system-wide predictions with date range filters and aggregations (`/api/v1/analytics/predictions/`).

---

## 4. Comprehensive Test Suite & Verification Matrix (163 Automated Tests)

Every component is governed by automated regression tests:

| Suite | Component | Test Count | Key Invariants Verified |
|---|---|---|---|
| **Backend Suite** | Django 5.2 | **45 passed** | CSRF enforcement on cookies, JWT rotation/blacklisting, user registration, property metadata, prediction persistence, admin security gates, contract drift |
| **Inference Suite** | FastAPI | **43 passed** | Liveness/readiness probes, schema version matching, Treatment B parking logic, carpet/super area conversion, invalid floor rejection, real artifact smoke tests |
| **ML Pipeline Suite** | Scikit-Learn / LightGBM | **75 passed** | 22-feature column transformer, missing value median imputation, unknown category encoding, non-negative prediction output |
| **Contract Suite** | OpenAPI 3.0.3 | **2 validated** | Zero specification errors across both `application-api.yaml` and `inference-api.yaml` |
| **Database Suite** | Django Migrations | **32 applied** | Clean zero-state database initialization without migration graph errors |

---

## 5. Phase 5 Roadmap (Next Steps for Tomorrow)

Tomorrow we will initiate **Phase 5: Next.js Frontend**.
1. **Scaffold Next.js 16 LTS:** Setup App Router, TypeScript, modern CSS framework, and clean API client gateway.
2. **Auth Integration:** Build Login, Register, Logout, and Token Refresh with CSRF bootstrap.
3. **Valuation Calculator UI:** Interactive property form with location select, dynamic area basis toggles, instant INR price estimation, and formatted Lakhs/Crores display.
4. **User Dashboard & History:** Recent valuations table, deletion actions, and export preview.
5. **Admin Operations View:** Analytics summary, system activity, and model health monitor.
