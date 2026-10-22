# Testing Plan & Strategy

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Status | Planning Draft — Phase 0 Boundary |
| Scope | Unit, Integration, End-to-End, and ML Quality Testing |

---

## 1. Test Levels & Methodologies

1. **Unit Testing:**
   - **Frontend:** Component tests, hook tests, utility/API client tests (Jest / Vitest + React Testing Library).
   - **Backend:** Django model validation, serializer validation, permission check tests (`pytest` + `pytest-django`).
   - **Inference Service:** FastAPI endpoint schemas, readiness logic, handling of missing artifacts (`pytest` + `httpx`).
   - **ML Training:** Deterministic price parser tests, area unit conversions, leakage checks.
2. **Integration / Contract Testing:**
   - Validate HTTP API responses against `contracts/application-api.yaml` and `contracts/inference-api.yaml`.
   - Verify Django prediction orchestration calling the standalone inference service.
3. **End-to-End (E2E) Testing:**
   - Visitor registration -> Login -> Enter property -> Receive INR estimate -> Persist in history -> View history -> Logout.
   - Negative security tests: non-admin attempting admin routes; user attempting to fetch another user's prediction history ID.
4. **Machine Learning Verification:**
   - Deterministic smoke tests on saved pipeline artifact.
   - Validation that predicted output is finite, numeric, positive, and formatted in INR.
   - Baseline comparison: verify MAE on test set is tracked against DummyRegressor.

---

## 2. Test Execution Commands (Local)

- **Frontend:** `npm test` / `npm run lint` / `npm run typecheck`
- **Backend:** `pytest` (inside `backend/.venv`)
- **Inference Service:** `pytest` (inside `inference-service/.venv`)
- **ML Training:** `pytest` (inside `ml/training/.venv`)
- **Scaffold Verification:** `powershell -ExecutionPolicy Bypass -File scripts/check_scaffold.ps1`
