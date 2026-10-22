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
- [ ] Full smoke test: user registration, login, price prediction, history storage, admin reporting.
