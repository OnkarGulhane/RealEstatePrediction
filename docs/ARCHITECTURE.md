# System Architecture Documentation

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Product | Real Estate Price Prediction Platform |
| Status | Scaffold State — Phase 0 Planning |
| Last updated | 22 October 2026 |
| Target environments | Local-first (Windows 11), future production deployment |

---

## 1. Architectural Philosophy & Principles

1. **Independent Deployability:** Frontend (`frontend/`), application backend (`backend/`), and inference service (`inference-service/`) are distinct applications with their own dependencies, entry points, configuration, and test suites.
2. **Clear Boundaries:** Services communicate exclusively over documented HTTP APIs (OpenAPI). Direct runtime code imports across services are prohibited.
3. **Decoupled Machine Learning:** 
   - Model training, data audit, and evaluation are executed strictly **offline** in `ml/training/`.
   - The online inference service loads an already approved, immutable pipeline artifact (`.joblib`) into memory at startup.
   - User prediction requests NEVER trigger training, fitting, or retraining.
4. **Data Ownership & Isolation:** The Django REST backend owns the application database (users, profiles, predictions, reports). The inference service does not access the database.
5. **No Direct Client Bypass:** The browser/frontend talks only to the Django backend. The internal inference service is protected behind private networking or service authentication.

---

## 2. Logical Topology

```text
       Browser / Client (Desktop & Mobile)
                        │
                        ▼ [HTTP / JSON]
         ┌───────────────────────────────┐
         │ Next.js + TypeScript Frontend │  Port: 3000
         │ (App Router, Tailwind/CSS)    │
         └──────────────┬────────────────┘
                        │
                        ▼ [HTTP / JSON API: /api/v1/...]
         ┌───────────────────────────────┐
         │ Django REST Framework Backend │  Port: 8000
         │ (Auth, DB, Business Logic)    │
         └───────┬──────────────┬────────┘
                 │              │
                 │ [Protected   │ [Django ORM]
                 │  HTTP API]   ▼
                 │        ┌───────────────────┐
                 │        │ Application DB    │ (SQLite dev /
                 │        │ (Users, History)  │  PostgreSQL prod)
                 │        └───────────────────┘
                 ▼
  ┌───────────────────────────────┐
  │ Independent Inference Service │  Port: 8001
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

## 3. Technology Choices and Decisions

| Component | Technology | Rationale | Status |
|---|---|---|---|
| **Frontend** | Next.js (App Router) + TypeScript | Modern responsive UI, type safety, modular routing, clean API client integration. | Approved |
| **Application Backend** | Python + Django REST Framework | Robust built-in user management, secure password hashing, ORM migrations, admin capabilities. | Approved |
| **Inference Service** | Python + FastAPI | Lightweight, high-throughput asynchronous execution, native Pydantic schema validation. | **PROVISIONAL / REQUIRES OWNER APPROVAL** |
| **Offline ML Training** | Python, pandas, NumPy, scikit-learn | Reproducible data cleaning, column transformers, and regression pipelines. | Approved |
| **Artifact Format** | `joblib` + `metadata.json` | Persists fitted preprocessing + estimator together to prevent training/serving skew. | Approved |
| **Local Database** | SQLite | Zero-configuration local development. | Approved for dev |
| **Production Database** | PostgreSQL | Robust concurrency, relational integrity, enterprise hosting support. | Planned for Phase 8 |

---

## 4. Local Default Port Map

| Service | Protocol | Local Address | Purpose |
|---|---|---|---|
| Frontend | HTTP | `http://localhost:3000` | Web application user interface |
| Application Backend | HTTP | `http://localhost:8000/api/v1` | Public REST API endpoints |
| Inference Service | HTTP | `http://localhost:8001` | Protected model prediction & health endpoints |
