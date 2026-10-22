# Real Estate Price Prediction Platform — Implementation Plan

| Field | Value |
|---|---|
| Document | Implementation Plan |
| Version | 1.3 — Phase 2 implementation complete (ready for review) |
| Product | Real Estate Price Prediction Platform — India |
| Related documents | `docs/PRD.md`, `docs/SRS.md`, `docs/ARCHITECTURE.md`, `docs/DATASET_ML_SPEC.md`, `docs/TESTING_PLAN.md` |
| Delivery strategy | Phase-gated; local-first; deploy online only after local acceptance |
| Current status | Phase 2 implementation complete — ready for owner review (Phase 0 and Phase 1 approved by product owner) |
| Last reviewed | 22 October 2026 |
| Project owner approval | Phase 0 and Phase 1 Approved; Phase 2 Pending |

> This plan defines the execution sequence, deliverables, verification evidence, and approval gates. It does not mean that any phase has been implemented or passed. Do not start coding until Phase 0 decisions and scope are approved. Do not begin a later phase until the current phase is accepted by the project owner.

> **Repository convention:** In the actual project repository, keep governing documents under `docs/` (`docs/PRD.md`, `docs/SRS.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/DATASET_ML_SPEC.md`, `docs/TESTING_PLAN.md`, and `docs/DEPLOYMENT_GUIDE.md`). Downloaded copies may be stored elsewhere until the repository is initialized.

---

## 1. Project Working Agreement

1. **`docs/PRD.md` defines product intent and scope.** `docs/SRS.md` defines detailed and testable software requirements. This file defines how work will be executed phase by phase.
2. **One active phase at a time.** Work only on the approved phase scope. Do not implement future phases preemptively.
3. **Inspect before editing.** At the start of each phase, inspect the repository, current files, environment, and previous phase status. Do not overwrite or regenerate existing work without understanding it.
4. **Plan before implementation.** State the tasks, impacted requirements, likely files, dependencies, and tests for the current phase before making changes.
5. **Run tests and report actual evidence.** Never claim a test passed unless it was actually executed and passed. If execution is blocked, label it `NOT RUN` and explain why.
6. **Fix current-phase defects before requesting approval.** Do not hide warnings, skip failing tests, or silently change requirements to make a test pass.
7. **No fabricated ML outputs.** Dataset counts, model scores, feature importance, and prediction results must come from actual runs. Synthetic data, if ever used for test fixtures, must be labelled as synthetic and must not be represented as real market data.
8. **Keep service boundaries.** Next.js communicates with Django over HTTP; Django communicates with the inference service over HTTP. Services must not import each other's application code at runtime.
9. **Protect data and secrets.** Do not commit `.env` files, credentials, private database files, unauthorized data, or model artifacts whose redistribution rights are unverified.
10. **Owner approval is a hard gate.** End every phase with a summary and explicit request for approval. Stop there until the project owner approves continuing.

## 2. Target Repository and Service Boundaries

The approved target architecture is a monorepo with independently runnable components:

- `frontend/`: Next.js (16.x LTS) + TypeScript user interface.
- `backend/`: Python + Django (5.2 LTS) REST Framework application API, authentication, persistence, history, admin/reporting.
- `inference-service/`: separate Python HTTP service using **FastAPI** (approved) for loading the approved model pipeline and generating estimates.
- `ml/training/`: offline data audit, cleaning, experimentation, training, evaluation, and candidate artifact creation.
- `contracts/`: versioned OpenAPI 3.0 contracts for Next.js ↔ Django and Django ↔ inference service.
- `docs/`: approved product, software, architecture, dataset/ML, testing, and deployment documents.

The inference service must not own user accounts or prediction history. Django owns those records. The browser must not call internal inference endpoints directly. Live user requests must never trigger model training.

## 3. Phase Status Board

All phases start as `NOT STARTED`. Status must be updated only from verified work.

| Phase | Focus | Status | Approval required |
|---|---|---|---|
| 0 | Requirements, architecture, and open decisions | APPROVED | Yes |
| 1 | Dataset audit and preparation rules | APPROVED | Yes |
| 2 | Offline ML training and evaluation | READY FOR REVIEW | Yes |
| 3 | Independent inference service | NOT STARTED | Yes |
| 4 | Django application backend | NOT STARTED | Yes |
| 5 | Next.js frontend | NOT STARTED | Yes |
| 6 | Cross-service integration and quality assurance | NOT STARTED | Yes |
| 7 | Reproducible local release | NOT STARTED | Yes |
| 8 | Online deployment | NOT STARTED | Yes |

Allowed statuses: `NOT STARTED`, `IN PROGRESS`, `BLOCKED`, `READY FOR REVIEW`, `APPROVED`, `REWORK REQUIRED`. A phase must not be marked `APPROVED` without recording evidence and owner approval.

## 4. Standard Cycle for Every Phase

Each phase follows the same execution loop:

1. **Entry check** — confirm previous phase approval and required inputs.
2. **Inspect** — review the repository and relevant documents; establish baseline state.
3. **Task plan** — list scope, SRS requirement IDs, proposed file changes, risks, and test commands.
4. **Implement** — make only approved changes for the current phase.
5. **Test** — execute the required tests, lint/type checks, data checks, and relevant manual cases.
6. **Fix and rerun** — fix current-phase failures and rerun affected and regression tests.
7. **Evidence report** — record changed files, commands executed, actual results, coverage where available, known limitations, and unresolved issues.
8. **Checkpoint** — review the diff and create a Git commit/checkpoint when version control is available. Keep secrets and restricted data out of the commit.
9. **Acceptance review** — compare results against the phase exit criteria and related SRS acceptance requirements.
10. **Stop for approval** — ask the project owner to accept the phase or request rework. Do not start the next phase automatically.

If the phase is blocked by a missing decision, dataset access, licence, dependency, or environment issue, report the blocker and stop work that depends on it. Do not guess a material decision silently.

---

## 5. Phase 0 — Requirements and Architecture Approval

### Objective

Confirm the product scope and decisions needed to start implementation without avoidable rework.

### Inputs

- `docs/PRD.md`
- `docs/SRS.md`
- `Real_Estate_Price_Prediction_FOLDER_STRUCTURE.md` or approved folder-tree definition
- Uploaded reference Word document and `house_prices.csv` audit findings

### Tasks

- [x] Review PRD, SRS, and folder structure for conflicts and stale references.
- [x] Confirm the monorepo boundary and independent lifecycle of frontend, backend, inference, and training.
- [x] Decide the inference framework: **FastAPI** approved for `inference-service/`; Django REST Framework remains the application backend.
- [x] Decide authentication approach for Next.js ↔ Django: **DRF + SimpleJWT** approved (short-lived in-memory access token, refresh token in HttpOnly cookie with rotation/revocation, authoritative backend authorization; implementation in Phase 4).
- [x] Agree API contract format and versioning: OpenAPI 3.0 YAML for both application API (`contracts/application-api.yaml`) and inference API (`contracts/inference-api.yaml`).
- [ ] Confirm dataset usage licence/provenance investigation owner and whether the raw dataset may be stored in the repository or redistributed (Pending Phase 1).
- [x] Confirm local runtime versions and dependency-management approach for Node.js and Python; pin/lock dependencies per service (Next.js 16.4.2, Django 5.2.18, DRF 3.18.3, SimpleJWT 5.5.1, FastAPI 0.115.14).
- [x] Confirm which P0 features must be included in the first local release and which P1 features may follow.
- [x] Create/update `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/DATASET_ML_SPEC.md`, `docs/TESTING_PLAN.md`, and `docs/FOLDER_STRUCTURE.md` as planning artifacts.
- [x] Record the unresolved decisions, chosen options, reasons, and any accepted risks in `docs/OPEN_DECISIONS.md`.

### Deliverables

- Approved PRD and SRS versions.
- Architecture decision record(s) for inference framework (FastAPI), auth strategy (SimpleJWT), API contracts (OpenAPI 3.0), and environment/dependency management.
- Approved canonical folder structure (`docs/FOLDER_STRUCTURE.md`) and phase plan.
- Open decisions list with owners and the last permissible phase for resolution (`docs/OPEN_DECISIONS.md`).

### Exit criteria

- No unresolved architecture conflict blocks Phase 1 or Phase 2.
- Inference framework is explicitly selected before Phase 3 implementation (FastAPI Approved).
- Dataset licence/provenance is either verified or a documented restriction is approved before the dataset/artifact is shared or redistributed (Pending Phase 1).
- Authentication decision is approved before Phase 4 authentication implementation (DRF + SimpleJWT Design Approved).
- Product owner approves Phase 0 deliverables.

### Requirements mapping

PRD Sections 2, 4, 6, 14, 16–17; SRS Sections 1–4, 14, 16–17.

---

## 6. Phase 1 — Dataset Audit and Preparation Rules

### Objective

Understand and validate the supplied dataset and approve the data-cleaning, feature, and split policies before training models.

### Tasks

- [x] Locate and record the exact original dataset source, downloaded version/date, citation/attribution, licence, and redistribution terms (Juhi Bhojani Kaggle lead; status UNVERIFIED / RESTRICTED FROM REDISTRIBUTION).
- [x] Produce a reproducible raw-data audit: file hashes, shape, column names/types, null counts, distinct values, location distribution, price distributions, and area-unit frequencies (`ml/training/src/real_estate_ml_training/audit.py`, `validate_data.py`).
- [x] Recompute the duplicate issue using clearly defined keys. Investigate repeated records after excluding `Index` (across all raw rows: 119,339 duplicates, 68,192 unique configurations; valid-target supervised subset: 112,592 duplicates, 65,255 unique eligible configurations). Phase 2 deduplicated training view policy approved; no rows deleted in Phase 1 output.
- [x] Define a deterministic parser for `Amount(in rupees)` including `Lac`, `Cr`, numeric values, invalid text, and `Call for Price` (177,847 valid supervised rows; 9,684 Call for Price; 0 unparseable; 100% reconciliation).
- [x] Inspect `Price (in rupees)` and other price-like fields for target leakage. Exclude `Price (in rupees)` and `Description` from prospective predictors.
- [x] Audit `Carpet Area`, `Super Area`, `Plot Area`, and `Dimensions`. Confirm unit conventions per record; convert only verified units (sqft, sqyrd, sqm). Strict separation: Carpet only (106,858), Super only (79,846), Both (0), Neither (827), Regional (30 preserved).
- [x] Review missingness, blank columns (`Dimensions` and `Plot Area` 100% blank; dropped), status near-constancy (99.67% Ready to Move), and extreme prices.
- [x] Save a reproducible audit report (`docs/PHASE1_DATASET_AUDIT_REPORT.md`) and sample non-sensitive summaries. Keep raw and prepared data local and excluded from Git.
- [ ] Implement Phase 2 deduplicated training view, feature encoding, location standardization, and validation splits (Deferred to Phase 2).

### Deliverables

- `docs/DATASET_ML_SPEC.md` updated with source, licence status, data dictionary, cleaning decisions, target definition, normalized area basis, features, exclusions, location policy, split plan, and known limitations.
- Reproducible audit script(s) under `ml/training/`.
- Raw/interim/processed-data policy documented. No training artifact is required yet.
- Decision log for duplicates, prices, area conversions, outliers, and missing features.

### Required checks

- Audit reproducible from the original file.
- Row/column counts reconcile at every cleaning stage.
- Price and area conversions have deterministic tests and documented examples.
- Duplicate policy has evidence and is not based only on an arbitrary row count.
- Potential leakage fields are explicitly documented.
- Licence/provenance status is clear; unresolved restrictions block public redistribution.

### Exit criteria

- Data dictionary, cleaning rules, target definition, area policy, duplicate policy, location handling, and split policy approved by the product owner.
- All remaining parse failures and data-quality limitations are quantified and documented.
- Phase 1 tests/audit checks pass.

### Requirements mapping

SRS: FR-ML-001 to FR-ML-006, data-validation and dataset-provenance requirements.

---

## 7. Phase 2 — Offline ML Training and Evaluation

### Objective

Train and fairly compare models using the approved dataset rules, then produce a versioned candidate pipeline and evaluation evidence.

### Tasks

- [x] Set up an isolated training environment and record dependency versions (scikit-learn 1.9.1, pandas 2.2.3, numpy 2.4.3, joblib 1.6.0).
- [x] Implement reproducible preprocessing using fitted transformers within a scikit-learn `Pipeline`/`ColumnTransformer` (`PropertyFeatureExtractor`, `ColumnTransformer`).
- [x] Establish a `DummyRegressor` baseline (median strategy: ₹62.52 Lakh Test MAE).
- [x] Train and compare appropriate regression candidates, subject to data quality and runtime: Linear/Ridge Regression, Decision Tree Regressor, Random Forest Regressor, and HistGradientBoosting Regressor.
- [x] Tune candidate models without using the holdout test set for selection. Preserve a fixed holdout partition (9,789 rows, 15%, seed=42) scored strictly post-freeze for Treatment B; record historical Treatment A exposure of this split as a documented limitation.
- [x] Record MAE, RMSE, and R² on the test set; compare against the baseline and document segment/city-level results where sample sizes support responsible interpretation.
- [x] Evaluate residuals and unrealistic errors. Review performance across supported locations and property segments rather than relying on a single overall metric.
- [x] Assess the proposed target of at least 10% MAE improvement over the baseline (Achieved: +56.91% improvement; winning tuned model Test MAE ₹26.94 Lakh; see `docs/PHASE2_MODEL_EVALUATION_REPORT.md`).
- [x] Save the fitted preprocessing + estimator as one versioned artifact where feasible. Create metadata with target, feature schema, units, dataset version/hash/reference, split seed, dependency versions, metrics, training timestamp, and known limitations (`experiments/phase2/model_pipeline.joblib`, `metadata.json`).
- [x] Create a model load/predict smoke test and verify predictions are finite, numeric, and consistent with the approved schema (`test_phase2_training.py`).
- [x] Create a promotion step that validates candidate metadata/artifact before it is published to the inference service (`scripts/promote_model.py`).

### Deliverables

- Training code and reproducible configuration.
- Model comparison and evaluation report.
- Candidate `model_pipeline.joblib` (or documented equivalent) and `metadata.json` generated by a real training run.
- Baseline and segment/city evaluation where supported.
- Tests covering preprocessing, training outputs, serialization/load, and prediction sanity.

### Exit criteria

- Training and evaluation are reproducible with recorded configuration/seeds.
- No known target leakage contaminates the final evaluation.
- Baseline and winning candidate are compared on the same fixed holdout test partition (historical Treatment A exposure documented).
- Metrics and limitations are recorded; the model is not described as accurate beyond the evidence.
- Artifact and metadata load successfully in a clean inference-compatible environment.
- Product owner reviews and approves the candidate model or requests rework.

### Requirements mapping

SRS: FR-ML-007 to FR-ML-013, model evaluation and artifact acceptance criteria.

---

## 8. Phase 3 — Independent Inference Service

### Objective

Build a separately runnable/deployable prediction service that loads an approved artifact once and returns validated estimates without training at request time.

### Dependencies

- Phase 0 inference framework decision approved.
- Phase 2 approved candidate artifact and metadata available.
- `contracts/inference-api.yaml` agreed with Django backend requirements.

### Tasks

- [ ] Create an independent Python application with its own dependency file, environment example, configuration, README, tests, and start command.
- [ ] Implement health and readiness endpoints; readiness must reflect artifact/config compatibility.
- [ ] Implement request/response schema validation using the approved feature contract.
- [ ] Load the model pipeline at application startup (not once per request, unless a documented need requires otherwise).
- [ ] Implement prediction logic that uses the same fitted preprocessing saved with the estimator.
- [ ] Validate outputs: numeric, finite, expected units, and policy for invalid/negative predictions. Do not fabricate fallback prices.
- [ ] Return consistent machine-readable errors for schema errors, unsupported inputs, missing/incompatible artifacts, and internal failures; never expose stack traces or secrets.
- [ ] Protect internal prediction endpoints using private networking and/or service-to-service authentication before deployment.
- [ ] Add timeouts and bounded behavior in the calling client contract; ensure health checks do not expose sensitive information.
- [ ] Verify the service can start and be tested without importing Django application code or using the Django database.

### Deliverables

- Independent inference service and runtime requirements.
- Versioned OpenAPI contract.
- Artifact metadata validation and readiness behavior.
- Unit/API tests and runbook.

### Exit criteria

- Service starts independently on local development configuration.
- Valid request returns a valid prediction for the approved feature schema.
- Invalid requests and missing/incompatible artifact scenarios return defined failures.
- Artifact loads once and training is never triggered by an inference request.
- Internal endpoint protection is demonstrated in test/deployment configuration.
- Product owner approves Phase 3.

### Requirements mapping

SRS: FR-INF-001 to FR-INF-009, NFR-MOD, NFR-REL, NFR-SEC, NFR-OBS as relevant.

---

## 9. Phase 4 — Django REST Application Backend

### Objective

Implement the application API and data persistence. Django owns authentication, user roles, prediction records, admin operations, and frontend-facing API responses.

### Dependencies

- Phase 0 authentication and API-contract decisions approved.
- Inference API contract available; inference implementation may be mocked only in isolated backend unit tests. Integrated behavior must be tested against the real service by Phase 6.

### Tasks

- [ ] Establish the Django project, settings structure, migrations, environment configuration, logging, and separate runtime dependencies.
- [ ] Implement registration, login, logout, current-user/profile operations, and administrator provisioning according to the approved auth design.
- [ ] Enforce authorization server-side; users must not edit their role or administrative flags through ordinary profile APIs.
- [ ] Define database models and indexes for prediction records, normalized input snapshots, numeric INR outputs, timestamps, model version, and correlation ID where available.
- [ ] Implement locations/input metadata endpoint from the approved supported-location/feature source.
- [ ] Implement prediction orchestration: validate user request, call the inference API over HTTP, validate response, persist only successful valid predictions, and return a documented response.
- [ ] Add robust timeout, unavailable-service, malformed-response, and retry behavior. Ensure retries cannot create duplicate successful history records.
- [ ] Implement paginated personal history with object-level ownership checks.
- [ ] Implement admin summary, user management, prediction records, date-range reports, model information, and P1 CSV export/analytics according to priority.
- [ ] Implement consistent JSON error shapes, request limits, pagination caps, authentication throttles/rate limits as approved, and API version prefix.
- [ ] Generate/update OpenAPI contract and keep it synchronized with implementation.
- [ ] Add automated unit, API, permission, ownership, input-validation, date-filter, and export-safety tests.

### Deliverables

- Independently runnable Django backend.
- Database models/migrations and environment template.
- Application OpenAPI contract.
- API test suite and backend runbook.

### Exit criteria

- Migrations apply from a clean local database.
- Authentication and all protected endpoints follow the approved strategy.
- Cross-user history access and non-admin access to admin operations are denied by server-side tests.
- Prediction API handles valid, invalid, timeout, unavailable-service, and malformed-inference-response cases safely.
- History/report pagination and date filtering tests pass.
- Product owner approves Phase 4.

### Requirements mapping

SRS: FR-AUTH, FR-HIST, FR-ADM, FR-API and applicable NFRs.

---

## 10. Phase 5 — Next.js Frontend

### Objective

Build the responsive user interface and connect it to the documented Django application API without bypassing the backend.

### Tasks

- [ ] Establish a Next.js + TypeScript app with separate lint, type-check, unit/component test, and build commands.
- [ ] Implement public homepage, project/how-it-works/model limitations information, login, registration, and profile pages.
- [ ] Implement the property prediction form based only on the approved input schema, normalized area definition, units, and supported location options.
- [ ] Implement loading, success, empty, validation-error, unauthorized, server-error, and inference-unavailable states.
- [ ] Implement result view showing numeric INR-backed display, property summary, disclaimer, model limitations, and optional supported derived metrics.
- [ ] Implement paginated prediction history and detail view, using server authorization as the source of truth.
- [ ] Implement admin dashboard, user/prediction tables, date-filtered reports, charts, model information, and authorized export workflows based on P0/P1 priorities.
- [ ] Build a reusable API client driven by environment configuration; do not hard-code service URLs in components.
- [ ] Ensure the browser never calls the internal inference API directly and secrets are never placed in client bundles.
- [ ] Provide accessible labels, keyboard focus, responsive layouts, clear error messages, and chart text summaries.
- [ ] Add component tests, form validation tests, and frontend type/lint/build checks.

### Deliverables

- Responsive Next.js frontend.
- Environment example and frontend README.
- Component/unit tests and screenshots or review evidence for main pages if useful.

### Exit criteria

- Required pages render and navigation works.
- Main user flows call actual Django APIs via the approved contract.
- Success, empty, validation, authorization, and service-failure states are handled.
- Frontend does not expose internal inference routes or secrets.
- Type checks, lint, component tests, and production build pass.
- Product owner approves Phase 5.

### Requirements mapping

SRS: FR-GEN, frontend aspects of FR-AUTH/FR-PRED/FR-HIST/FR-ADM, NFR-UX.

---

## 11. Phase 6 — Integration, API Testing, Security, and Quality Assurance

### Objective

Verify that the independently built components work together and that approved P0 requirements are satisfied end to end.

### Tasks

- [ ] Start frontend, backend, inference service, and database according to documented local setup.
- [ ] Execute application API and inference API contract tests against running services.
- [ ] Execute end-to-end flows: registration/login, valid prediction, saved history, history retrieval, sign-out, and denied protected access.
- [ ] Execute admin flows: dashboard, users, predictions, date-range report, and approved exports.
- [ ] Verify frontend → Django → inference → Django persistence → frontend response path.
- [ ] Test negative/edge inputs: missing fields, invalid types, negative/zero values according to approved rules, unsupported locations, unknown categories, and invalid area basis.
- [ ] Test degraded scenarios: inference down, timeout, unreadable/incompatible model artifact, malformed model response, database unavailable, and authorization failures.
- [ ] Test data isolation and privilege boundaries, including guessed/changed IDs and direct HTTP requests that bypass the UI.
- [ ] Test pagination, filter boundaries, date-range validation, CSV formula-injection handling, rate limits, CORS/CSRF/auth settings as applicable.
- [ ] Run dependency/security checks available in the selected toolchain; review secrets and Git ignore rules.
- [ ] Run regression tests after every defect fix and verify no unrelated requirement regressed.
- [ ] Record unresolved defects with severity, reproduction steps, and release decision. Critical/high security or P0 failures block acceptance.

### Deliverables

- `docs/TESTING_PLAN.md` and executed test report.
- API test collection or automated API test suite.
- Integration/end-to-end evidence and defect log.
- Updated traceability showing each P0 requirement is verified or explicitly blocked.

### Exit criteria

- All approved P0 acceptance checks pass; any environment-limited check is explicitly marked `NOT RUN`, not passed.
- No unresolved critical/high severity security defect remains.
- Authentication, ownership, admin permissions, prediction safety, model error handling, and persistence are verified.
- Test report states exact commands, environment, counts, results, and known limitations.
- Product owner approves Phase 6.

### Requirements mapping

SRS Section 13, all P0 requirements, and integration/security NFRs.

---

## 12. Phase 7 — Reproducible Local Release

### Objective

Package and document a release that can be set up and run from a clean local environment without relying on the original developer machine.

### Tasks

- [ ] Verify the repository's `.gitignore` excludes secrets, virtual environments, build outputs, local DBs where appropriate, raw restricted data, and unapproved model artifacts.
- [ ] Review dependency pins/lockfiles and runtime version documentation for every service.
- [ ] Provide `.env.example` files with safe placeholders and no real secrets.
- [ ] Provide root README and service READMEs with prerequisites, setup, environment configuration, database migrations, model artifact handling, start commands, test commands, and troubleshooting.
- [ ] Provide reproducible scripts for local setup/run where appropriate; scripts must fail clearly and not silently ignore errors.
- [ ] Verify startup ordering and readiness checks for the services. Optional Compose orchestration may be added if it simplifies the approved workflow.
- [ ] Test a fresh clone/copy setup using only documented files and approved dataset/artifacts.
- [ ] Create a release checklist and prepare a ZIP only after licence/security review. Do not include secrets, user data, or restricted raw data.
- [ ] Confirm local database setup, test accounts creation instructions, model artifact generation/promotion instructions, and reset/cleanup instructions.

### Deliverables

- Reproducible local repository state.
- Root and per-service documentation.
- Verified setup/test report.
- Release ZIP or release artifact only if requested/approved and redistribution rights permit it.

### Exit criteria

- A clean local setup follows documentation successfully.
- Each service can be started and tested independently.
- Required test suites run as documented and actual status is recorded.
- No secrets or unapproved restricted data are included in the release.
- Product owner approves local release.

### Requirements mapping

SRS FR-DOC and NFR-COMP/NFR-DEP requirements.

---

## 13. Phase 8 — Online Deployment

### Objective

Deploy the approved application with independently managed frontend, backend, inference service, and a persistent production database.

### Dependencies

- Phase 7 local release approved.
- Hosting/provider, domain/origins, production database, secrets mechanism, and budget/limits explicitly decided.
- Dataset and model-artifact distribution conditions reviewed.

### Tasks

- [ ] Select hosting for Next.js, Django, inference service, and PostgreSQL based on runtime support, persistence, networking, resource needs, and cost. Avoid choosing providers before compatibility is checked.
- [ ] Configure environment-specific settings and secret stores; do not reuse development secrets.
- [ ] Provision production database, apply migrations, and verify persistence/backups/retention appropriate to the hosting plan.
- [ ] Configure HTTPS, allowed frontend origins, secure cookie/CSRF/token settings, service-to-service protection, and safe logging.
- [ ] Deploy inference with the approved model artifact and validate readiness before enabling prediction traffic.
- [ ] Configure backend inference URL, bounded timeouts, and fail-safe error handling.
- [ ] Deploy frontend with the correct public application API base URL.
- [ ] Run production smoke tests for sign-in, property prediction, saved history, permission boundaries, and graceful inference failure.
- [ ] Verify logs, health checks, error handling, static assets, build output, and mobile/desktop behavior.
- [ ] Document deployment steps, rollback procedure, artifact promotion/rollback, and known limitations.

### Deliverables

- Deployed application and service URLs (if deployment is approved and available).
- Deployment guide, production smoke-test report, and rollback notes.

### Exit criteria

- Production smoke tests pass.
- HTTPS, secrets, database persistence, allowed origins, and inference service protection are verified.
- No critical/high security issue remains open.
- Product owner explicitly approves the deployment/release.

### Requirements mapping

SRS NFR-SEC, NFR-DEP and deployment acceptance requirements.

---

## 14. Mandatory API Testing Strategy

API testing is not a one-time activity at the end. It is required within the inference phase, backend phase, and full integration phase.

### Inference API tests (Phase 3)

- Valid payload and expected response schema.
- Missing/invalid fields, unsupported categories/locations, and invalid units.
- Artifact absent, corrupt, or incompatible.
- Readiness state before/after artifact load.
- Numeric, finite output and defined handling of invalid predictions.
- Internal endpoint access protection and safe error responses.

### Application API tests (Phase 4)

- Registration/login/logout/profile.
- Authentication required for protected endpoints.
- User ownership and administrator permission boundaries.
- Prediction request validation, valid inference response, timeout, malformed response, inference unavailable.
- Successful predictions saved once; failed predictions not saved as successes.
- History pagination, details, filters, date boundaries, user/admin reports and CSV export safety.
- Consistent status codes/error body and API contract compliance.

### Integrated API/end-to-end tests (Phase 6)

- Next.js calls Django; Django calls inference over HTTP; Django persists the result; frontend renders the returned result.
- Browser cannot bypass Django and call internal inference endpoint.
- Service-down and timeout cases show safe user-facing errors and do not fabricate or persist false successful estimates.
- Re-run API and regression tests after fixes.

### Proposed tools

- Backend/inference automated tests: pytest and/or Django REST Framework test utilities according to the chosen stack.
- Manual requests: Postman or Bruno.
- Contract documentation/validation: OpenAPI.
- Browser-level tests: a compatible end-to-end test runner chosen during Phase 0/5.

Tools are proposed; the exact dependency and runner choices must be recorded before implementation. Manual testing alone does not replace automated regression tests.

---

## 15. Phase Completion Report Template

At the end of every phase, produce a report using this template:

```text
Phase number and name:
Status: READY FOR REVIEW / BLOCKED / REWORK REQUIRED

Scope completed:
- [list tasks and SRS requirement IDs]

Files created/changed:
- [paths and brief reason]

Commands executed:
- [exact commands]

Test results:
- Passed: [count/list]
- Failed: [count/list]
- Not run: [list and reason]

Acceptance criteria:
- [criterion]: PASS / FAIL / NOT RUN, with evidence

Known issues/risks:
- [severity, reproduction steps, workaround if any]

Dependency/security notes:
- [relevant observations]

Checkpoint/commit:
- [identifier if available]

Recommendation:
- APPROVE PHASE / REWORK / BLOCKED

Project-owner decision:
- PENDING until explicit owner approval
```

A phase report must not use phrases such as “fully working” or “all tests passed” unless supported by actual execution evidence.

## 16. Change Control and Traceability

- Each implementation task shall reference relevant SRS requirement IDs.
- Changes to product goals, user-facing features, roles, or success measures update the PRD first.
- Changes to required behavior, validation, API schema, permissions, or test conditions update the SRS and relevant OpenAPI contract.
- Changes to service boundaries, dependencies, runtime, or deployment decisions update `docs/ARCHITECTURE.md` and the affected phase plan.
- Changes to source data, cleaning, feature schema, splitting, target, or metrics update `docs/DATASET_ML_SPEC.md` and the training report.
- Scope expansion during a phase requires explicit approval and an updated plan. Do not silently pull future-phase work into the current phase.
- Maintain traceability: `PRD outcome -> SRS requirement ID -> phase/task -> test -> evidence -> approval`.

## 17. Approved Architecture Decisions & Remaining Open Issues

### 17.1 Approved Architecture Decisions (Phase 0)
1. **Inference Framework:** **FastAPI** is approved for `inference-service/`.
2. **Authentication Design:** **DRF + SimpleJWT** approved (in-memory access JWT + HttpOnly refresh cookie, rotation/revocation, backend authoritative permissions; implementation in Phase 4).
3. **Database Strategy:** **SQLite** approved for local development; **PostgreSQL** approved and strictly required for production deployment (enforced via `config.settings.production` with no fallback to SQLite).
4. **Runtime Versions:** Pinned and verified: Next.js 16.4.2 (Active LTS), React 19.0.0, Django 5.2.18 LTS, DRF 3.18.3, SimpleJWT 5.5.1, FastAPI 0.115.14, Python 3.13.

### 17.2 Current Open Decisions (Pending Evidence or Relevant Phases)
1. **Dataset Provenance & Redistribution:** Verify original dataset licence, provenance, attribution, and redistribution permissions before any dataset publication (designated UNVERIFIED / RESTRICTED FROM REDISTRIBUTION; all data local-only).
2. **Duplicate-Record Policy:** **RESOLVED & EXECUTED (Phase 2):** Primary supervised view excludes exact 20-column duplicates (65,255 unique property configurations; 112,592 duplicate occurrences removed with auditable mapping; see `docs/DATASET_ML_SPEC.md` and `docs/OPEN_DECISIONS.md`).
3. **Price Parsing & Target Integrity:** **RESOLVED & VERIFIED (Phase 1):** Continuous asking price parsed in INR (177,847 valid supervised rows; 9,684 Call for Price rows excluded; 0 unparseable rows; see `docs/DATASET_ML_SPEC.md`).
4. **Area-Basis & Unit Policy:** **RESOLVED & EXECUTED (Phase 2):** Carpet Area and Super Area kept strictly separate with independent presence and verification indicators; unverified regional units excluded from numeric conversion (see `docs/DATASET_ML_SPEC.md`).
5. **Supported Location Aliases & Policy:** Behavior for 81 dataset location strings handled via `OneHotEncoder(handle_unknown='ignore')` in Phase 2; application-level location aliasing and validation pending Phase 3/4.
6. **Production Hosting Provider & Domain:** Choose production hosting provider and public domain after local acceptance tests (Phase 8).
7. **Data Retention & Privacy Policy:** Finalize user account deletion, prediction history TTL, and export policies before deployment (Phase 4/8).

A decision only blocks the phase that requires it, but must be resolved or explicitly accepted before that phase begins.

## 18. Definition of Done for the Entire Project

The project is ready for local release only when:

- All required P0 requirements have test evidence and pass their acceptance checks, or any exception is explicitly accepted and documented by the product owner.
- Dataset provenance/licence status, cleaning rules, feature schema, model metrics, baseline comparison, and limitations are documented.
- The model pipeline is reproducible, saved with metadata, and loaded by the independent inference service.
- Frontend, backend, and inference service can be started and tested independently.
- API testing, ownership/role tests, and critical end-to-end user flows pass.
- Error handling does not invent predictions or silently store failures as successes.
- Clean setup can follow the README without undocumented local state.
- Dependencies are recorded, configuration uses environment variables, and no secrets/restricted data are included in source control/release.
- Product owner has reviewed the final test report and explicitly approved local release.

Online deployment has an additional release gate: production configuration, HTTPS, protected inference access, database persistence, and production smoke tests must pass before declaring deployment complete.

---

## Approval Record

- Phase 0: **APPROVED** (Architecture alignment and scaffolding verified).
- Phase 1: **APPROVED** (Dataset audit, reconciliation accounting, and policy decisions finalized).
- Phase 2: **IMPLEMENTATION COMPLETE / READY FOR OWNER REVIEW**; owner approval remains **PENDING**.
- Phase 3: **NOT STARTED** and strictly not authorized until explicit Phase 2 owner approval.
- Next release gate: Await product owner review and authorization before initiating Phase 3 (FastAPI inference service).
