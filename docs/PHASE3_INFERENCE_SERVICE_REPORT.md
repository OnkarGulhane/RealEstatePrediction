# Phase 3 — Independent Inference Service Completion Report

**Phase number and name:** Phase 3 — Independent Inference Service
**Repository:** `OnkarGulhane/RealEstatePrediction`
**Execution Date:** 22 October 2026
**Status:** **READY FOR REVIEW** (Product Owner review pending)

---

## 1. Scope Completed

Implemented and verified the standalone FastAPI prediction microservice in `inference-service/` in strict conformance with `docs/SRS.md` requirements FR-INF-001 through FR-INF-009, `docs/ARCHITECTURE.md`, and the approved Phase 2 candidate model:

- **FR-INF-001 (Independent runtime):** Self-contained FastAPI application with its own pinned `requirements.txt`, environment template (`.env.example`), configuration, comprehensive test suite, and runbook. Operates independently with zero Django imports or application database dependencies.
- **FR-INF-002 (Model load once):** Loads and verifies the approved serialized scikit-learn pipeline once during FastAPI lifespan startup via `ModelLoader`.
- **FR-INF-003 (Readiness probe):** `GET /health/ready` returns `200 OK` with model version only when artifact and metadata are verified and compatible in memory; returns `503 Service Unavailable` with `status: not_ready` otherwise, without leaking system paths or tracebacks.
- **FR-INF-004 (Prediction endpoint):** `POST /api/v1/predict` accepts normalized schema 1.0 property inputs and returns real, finite, positive INR price estimates with active model version and correlation `request_id`.
- **FR-INF-005 (Schema validation):** Pydantic v2 schemas reject invalid schema versions, missing fields, non-finite values, invalid floor relationships, unsupported locations (`UNSUPPORTED_LOCATION`), and unapproved categories (`INVALID_CATEGORY`).
- **FR-INF-006 (Protected internal access):** Protected endpoints require internal service authentication via `X-Service-Token` header using constant-time `secrets.compare_digest`. Production mode rejects startup if `SERVICE_TOKEN` is unconfigured. Default host binds strictly to `127.0.0.1` (loopback).
- **FR-INF-007 (Artifact compatibility):** Validates metadata JSON, target currency (`INR`), exact 22-feature schema order, runtime library versions (scikit-learn, pandas, numpy, joblib), and pipeline structure before declaring readiness.
- **FR-INF-008 (Output sanity checks):** Validates model output is finite and strictly positive. Non-positive, zero, NaN, or infinite outputs trigger controlled 500 error `INVALID_MODEL_OUTPUT`; never fabricates fallback or dummy estimates.
- **FR-INF-009 (No training at inference):** Inference requests only execute the pre-fitted transformer and regressor; no encoders, imputers, or estimators are fitted at request time.

---

## 2. Files Created and Modified

| File Path | Nature | Purpose |
|---|---|---|
| `inference-service/app/config/settings.py` | Modified | Updated with `127.0.0.1` default bind, deterministic path resolver relative to service root, and production `SERVICE_TOKEN` validation |
| `inference-service/app/config/__init__.py` | Modified | Exported `settings`, `Settings`, and `SERVICE_ROOT` |
| `inference-service/app/model/loader.py` | Modified | Implemented `ModelLoader` with JSON metadata validation, 22-feature schema check, runtime compatibility checks, category extraction, thread-safe lifespan loading, and explicit dependency import verification |
| `inference-service/app/schemas/errors.py` | Created | Defined standard error envelope matching SRS Section 7.5 (`ErrorResponse`, `ErrorDetail`) |
| `inference-service/app/schemas/predict.py` | Modified | Implemented Pydantic v2 schemas for `PropertyPredictionRequest`, `PredictionResponse`, and health models with Treatment B parking semantics |
| `inference-service/app/schemas/__init__.py` | Modified | Exported request/response and error schemas |
| `inference-service/app/services/adapter.py` | Created | Implemented `RequestAdapter` to convert requests to 1-row DataFrames with Treatment B parking handling, area basis, all 4 area indicators, interval mapping, and categorical normalization |
| `inference-service/app/services/predict_service.py` | Modified | Implemented `PredictionService` with readiness check, DataFrame adaptation, single predict execution, and output sanity checks |
| `inference-service/app/services/__init__.py` | Modified | Exported prediction service and adapter |
| `inference-service/app/api/auth.py` | Created | Implemented `verify_service_token` dependency with constant-time token comparison |
| `inference-service/app/api/routes.py` | Modified | Implemented routes: `GET /health/live`, `GET /health/ready`, `POST /api/v1/predict`, and `GET /api/v1/model/metadata` |
| `inference-service/app/main.py` | Modified | Lifespan model loader, `X-Request-ID` correlation middleware, and standardized error envelope exception handlers |
| `inference-service/.env.example` | Modified | Documented loopback host, relative artifact paths, and `SERVICE_TOKEN` placeholder |
| `inference-service/requirements.txt` | Modified | Pinned scikit-learn (`1.9.1`), pandas (`2.2.3`), numpy (`2.4.3`), joblib (`1.6.0`), FastAPI, Uvicorn, Pydantic, and pytest |
| `inference-service/README.md` | Modified | Added Windows PowerShell runbook, configuration, endpoint examples, artifact copy/reference options, and troubleshooting guide |
| `contracts/inference-api.yaml` | Modified | Synchronized OpenAPI 3.0.3 contract with security schemes, request/response models, and error responses |
| `inference-service/tests/test_health.py` | Modified | Unit tests for process liveness and truthful readiness |
| `inference-service/tests/test_loader.py` | Created | Unit tests for metadata validation, feature schema order, version compatibility, deserialization safety, default paths, and allow-listed metadata |
| `inference-service/tests/test_adapter.py` | Created | Unit tests for RequestAdapter: area basis, Treatment B parking (0, None, count, > 20), floors, categories, and 22-feature schema order |
| `inference-service/tests/test_predict.py` | Created | Integration tests for predict endpoint: readiness guard, single predict invocation, validation errors, boundaries, output sanity, and error envelopes |
| `inference-service/tests/test_auth.py` | Created | Unit tests for `X-Service-Token` protection (valid, missing, invalid) and production startup validation |
| `inference-service/tests/test_contract_drift.py` | Created | Contract-to-implementation synchronization tests preventing schema drift |
| `inference-service/tests/test_real_smoke.py` | Created | End-to-end smoke test against the actual local Phase 2 candidate model artifact |
| `docs/PHASE2_MODEL_EVALUATION_REPORT.md` | Modified | Updated review labels to reflect Phase 2 Product Owner approval on 22 October 2026 |
| `docs/DATASET_ML_SPEC.md` | Modified | Updated review labels to reflect Phase 2 Product Owner approval on 22 October 2026 |
| `docs/IMPLEMENTATION_PLAN.md` | Modified | Recorded Phase 2 as Approved, marked Phase 3 tasks completed, updated Approval Record |
| `docs/PHASE3_INFERENCE_SERVICE_REPORT.md` | Created | This Phase 3 completion report |

---

## 3. Dependency & Artifact Verification

- **Local Model Artifact:** `ml/training/experiments/phase2/model_pipeline.joblib` (1,103,840 bytes, Git-ignored, verified present).
- **Local Metadata:** `ml/training/experiments/phase2/metadata.json` (8,839 bytes, Git-ignored, verified present).
- **Promotion Script Audit:** `ml/training/scripts/promote_model.py` was inspected and verified to perform integrity and metric validation; it does not copy or move files.
- **Runtime Dependency Compatibility:**
  - `scikit-learn`: Recorded `1.9.1` | Installed `1.9.1` (COMPATIBLE)
  - `pandas`: Recorded `2.2.3` | Installed `2.2.3` (COMPATIBLE)
  - `numpy`: Recorded `2.4.3` | Installed `2.4.3` (COMPATIBLE)
  - `joblib`: Recorded `1.6.0` | Installed `1.6.0` (COMPATIBLE)
  - `python`: Recorded `3.13.5` | Installed `3.13.5` (COMPATIBLE)
- **Import Resolution:** Package `real_estate_ml_training` is cleanly and deterministically resolvable by `ModelLoader` dynamically relative to `SERVICE_ROOT` (`SERVICE_ROOT.parent / "ml" / "training" / "src"`). Machine-specific absolute `.pth` files are not required.

---

## 4. Commands Executed & Test Results

### Command 1: Inference Service Automated Test Suite
```powershell
$env:PYTHONPATH="inference-service"; .\inference-service\.venv\Scripts\python.exe -m pytest inference-service/tests -v
```
**Outcome:** Exited with code `0`.
**Results:** **40 passed**, 0 failed, 0 skipped in 1.89s.
- `test_adapter.py`: 9 passed (carpet/super area, Treatment B parking 0/None/count/ambiguous, floors, categorical normalization, unsupported location, invalid category, bathroom interval, exact 22-feature schema order)
- `test_auth.py`: 5 passed (matching token allowed, missing token 401, invalid token 403, health unauthenticated, production setting validation)
- `test_contract_drift.py`: 4 passed (YAML parse, path/operations sync, request schema field match, security scheme application)
- `test_health.py`: 3 passed (liveness 200, readiness 503 when unloaded, readiness 200 when loaded)
- `test_loader.py`: 10 passed (missing artifact, missing metadata, corrupt JSON, target unit != INR, feature schema mismatch, version incompatibility, corrupt deserialization, missing predict, allow-listed metadata without leakage, default configured paths)
- `test_predict.py`: 8 passed (model not ready 503, valid call single invocation, schema version != 1.0 rejected 422, invalid area values 422, invalid floor relationship 422, unsupported location 422, invalid category 422, non-positive/non-finite output 500)
- `test_real_smoke.py`: 1 passed (end-to-end smoke test against actual local Phase 2 candidate model)

### Command 2: ML Training Regression Test Suite
```powershell
python -m pytest ml/training/tests -q
```
**Outcome:** Exited with code `0`.
**Results:** **75 passed**, 0 failed in 1.71s (zero regressions across all Phase 1 and Phase 2 offline ML tests).

### Command 3: Contract Validation
- **YAML Syntax:** `yaml.safe_load(open('contracts/inference-api.yaml'))` executed with code `0` (valid YAML).
- **Automated Drift Verification:** `test_contract_drift.py` verified exact synchronization with routes and Pydantic schemas (4/4 passed).
- **External CLI Semantic Validator:** **PASSED** (executed `.\inference-service\.venv\Scripts\openapi-spec-validator.exe contracts\inference-api.yaml`, returned `contracts\inference-api.yaml: OK` with exit code `0`).

---

## 5. Actual-Model Smoke Test Evidence

Executed locally against `ml/training/experiments/phase2/model_pipeline.joblib`:

- **Input Property:**
  - Location: `Thane`
  - Area: `1200.0 sqft` (Carpet basis)
  - BHK: `2`
  - Bathrooms: `2.0`
  - Balcony: `1`
  - Parking: `1.0` (Treatment B)
  - Furnishing: `Semi-Furnished`
  - Transaction: `Resale`
  - Status: `Ready to Move`
  - Facing: `East`
  - Ownership: `Freehold`
- **Output Response:**
  - HTTP Status: `200 OK`
  - `estimated_price_inr`: `8316392.49` (₹83.16 Lakh)
  - `currency`: `INR`
  - `model_version`: `real_estate_hist_gradient_boosting_log_tuned_v1`
  - `schema_version`: `1.0`
  - Output Sanity: Strictly positive, finite, no clipping, no fallback fabrication.

---

## 6. Acceptance Criteria Summary

| Acceptance Criterion | Result | Evidence |
|---|---|---|
| Service starts independently on local development configuration | **PASS** | Uvicorn starts on `127.0.0.1:8001`, `GET /health/live` returns `200 OK` |
| Valid request returns a valid prediction for approved feature schema | **PASS** | `POST /api/v1/predict` returns ₹8,316,392.49 with active model version |
| Invalid requests and missing/incompatible artifact scenarios return defined failures | **PASS** | 422 for schema/category/location errors; 503 for unloaded model; tested in 18 distinct scenarios |
| Artifact loads once and training is never triggered by an inference request | **PASS** | Model loaded once in lifespan startup; `predict()` called directly on fitted pipeline; zero training at request time |
| Internal endpoint protection is demonstrated in test/deployment configuration | **PASS** | `X-Service-Token` enforced with constant-time check; production startup rejects missing token |
| No secrets, raw CSVs, or binary artifacts committed | **PASS** | Git status clean of artifacts; `.joblib`, `.json` metadata, `.env`, and venvs ignored |

---

## 7. Known Issues & Boundaries

1. **Local-Only Artifacts:** Model artifact (`model_pipeline.joblib`) and metadata (`metadata.json`) remain local-only and Git-ignored. Remote environments must provide matching Phase 2 artifacts via secure deployment pipelines.
2. **Direct Browser Calls Prohibited:** The inference service is strictly an internal service intended for Django backend consumption. Public browser-to-inference access is prohibited by architecture.
3. **Phase 4 & Phase 5 Status:** Django backend (Phase 4) and Next.js frontend (Phase 5) are **NOT STARTED** and strictly not authorized until explicit Product Owner review and approval of Phase 3.

---

## 8. Recommendation

**READY FOR OWNER REVIEW.**

Phase 3 inference service implementation is complete, independently runnable, fully tested (40/40 inference tests, 75/75 training regression tests), verified against the real Phase 2 model artifact, and conforms strictly to all architectural and security boundaries.

**Product Owner Decision:** **PENDING** until explicit owner decision.
