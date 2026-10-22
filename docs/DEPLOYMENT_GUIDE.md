# Deployment Guide (Planned Phase 8)

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Status | Planning Draft — Local-First Phase |
| Deployment Phase | Phase 8 (Post-Local Verification) |

---

## 1. Deployment Philosophy

1. **Local-First Verification:** No online deployment will be attempted until all P0 local acceptance tests, data audits, and security boundaries pass completely in Phase 7.
2. **Independent Deployability:**
   - Frontend: Static export or Next.js Node server (e.g., Vercel or cloud container).
   - Backend: Django WSGI/ASGI service with Gunicorn or Uvicorn (e.g., Render, Railway, AWS ECS).
   - Inference Service: Independent container with pinned scikit-learn and model artifact.
   - Database: Managed PostgreSQL with SSL enabled.
3. **Zero Secrets in Code:** All database credentials, JWT secrets, and API keys are injected via platform secret managers.

---

## 2. Production Smoke Check Checklist

Prior to declaring production release complete, the following checks must pass:
- [ ] HTTPS enforced across all public endpoints.
- [ ] CORS restricted strictly to the production frontend domain.
- [ ] Internal inference endpoint protected from anonymous public internet traffic.
- [ ] Production database migrations applied and persistent.
- [ ] PostgreSQL connection verified with SSL enabled.
- [ ] Full smoke test: user registration, login, price prediction, history storage, admin reporting.

---

## 3. Containerization & Docker Compose Status

- **Architectural Blueprint:** `compose.yaml` is provided at the repository root as a reference deployment blueprint.
- **Current Runnable Status:** Compose is **NOT YET RUNNABLE** in Phase 0 because service Dockerfiles (`frontend/Dockerfile`, `backend/Dockerfile`, `inference-service/Dockerfile`) have not yet been authored.
- **Local Development Recommendation:** Do NOT rely on Docker for local development. Use the documented native PowerShell environment (`scripts/setup_dev.ps1` and `scripts/run_local.ps1`). Dockerfiles will be added and verified in Phase 8 deployment preparation.

---

## 4. Production Database Configuration Enforcement

- Production strictly requires **PostgreSQL**.
- Under `backend/config/settings/production.py`, the configuration inspects environment variables: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, and `POSTGRES_PORT`.
- If any required database variable is missing, `django.core.exceptions.ImproperlyConfigured` is raised immediately.
- **No SQLite Fallback:** Silent fallback to SQLite in production settings is explicitly prohibited to prevent silent data loss.
