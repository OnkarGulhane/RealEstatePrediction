# Software Requirements Specification (SRS)

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Product | Real Estate Price Prediction Platform |
| Document | Software Requirements Specification (SRS) |
| Version | 1.0 — Review Draft |
| Status | Ready for product-owner review; not yet approved for implementation |
| Prepared on | 22 October 2026 |
| Primary audience | Product owner, frontend developer, backend developer, ML developer, tester, project evaluator |
| Parent document | `PRD.md` — Real Estate Price Prediction Platform |
| Architecture | Next.js frontend + Django REST Framework backend + independently deployable Python inference service + offline ML training |
| Delivery approach | Local-first, phase-gated development; online deployment only after local release acceptance |

> **Important status statement:** This SRS defines expected system behavior and testable requirements. It does not claim that the system has been implemented or tested. No phase is complete until its specified checks pass and the product owner approves progression. Requirements dependent on the dataset audit or unresolved architecture decisions are explicitly marked as provisional/pending.

---

## 1. Purpose

This SRS converts the product-level goals in `PRD.md` into software requirements that can be designed, implemented, tested, and reviewed. It defines system boundaries, user roles, functional behavior, data rules, machine-learning requirements, external interfaces, security expectations, non-functional requirements, acceptance criteria, and phase exit gates.

The system will estimate residential property **listing prices** in Indian Rupees (INR), using supported property features and a trained regression pipeline. The estimate is not a certified valuation or guaranteed final transaction price.

### 1.1 How to use this SRS

- Use `PRD.md` to understand **why** the product exists, its audience, scope, priorities, and product outcomes.
- Use this `SRS.md` to implement and verify **what the software shall do**.
- Use `ARCHITECTURE.md` to document service-level design decisions, deployment boundaries, and component interactions.
- Use `IMPLEMENTATION_PLAN.md` to track phase tasks, dependencies, evidence, open issues, and approvals.
- Use `DATASET_ML_SPEC.md` to record the actual dataset audit, data dictionary, conversion rules, model experiments, and measured results.
- Do not start a new phase until the current phase's exit gate has been reviewed and explicitly approved.

### 1.2 Requirement language

The terms **shall**, **must**, and **required** indicate mandatory requirements. **Should** indicates a strong recommendation that may be waived only with a documented reason. **May** indicates an optional capability. A requirement marked **Pending** must be resolved or explicitly accepted before the phase that depends on it starts.

---

## 2. Reference Documents and Source Boundaries

1. `PRD.md` — the product scope and high-level decisions approved by the product owner.
2. User-provided reference document, *Real Estate Price Prediction Using Python and ML* — source for the original concepts of registration/login, profile management, price prediction, prediction history, admin dashboard, user management, prediction records, and date-range reports. The agreed product architecture intentionally replaces the reference document's Django-rendered frontend with Next.js and a separate API backend.
3. User-provided archive `archive.zip`, containing `house_prices.csv` — source of the preliminary dataset audit figures in Section 8.1. These must be reproducible by the project audit script before model training is approved.
4. Candidate source page: https://www.kaggle.com/datasets/juhibhojani/house-price — provenance and licence still require direct verification. The presence of a public page does not automatically permit redistribution of the downloaded data.

If this SRS and the approved PRD conflict, the product owner shall resolve the conflict and update the documents. The source Word document is a feature reference, not a reason to override the later-approved Next.js/API architecture.

---

## 3. Scope

### 3.1 In scope

- Responsive Next.js website for visitors, registered users, and administrators.
- Account registration, authentication, logout, and permitted profile management.
- Property input form using only verified fields supported by the approved dataset and model schema.
- INR listing-price estimation using a trained and approved regression pipeline.
- Successful prediction persistence and user-owned prediction history.
- Admin dashboard, user management, prediction records, date-filtered reports, and actual-data analytics.
- CSV export of approved report fields for authorized administrators.
- Separate Django REST Framework application backend.
- Separate Python inference service exposed over an HTTP API.
- Offline ML training, reproducible data preparation, model comparison, evaluation, and artifact release.
- Service-level tests, contract tests, integration tests, end-to-end tests, documentation, and local release checks.
- Online deployment only after local acceptance criteria pass.

### 3.2 Out of scope for the first release

- Guaranteed sale price, legally certified valuation, bank valuation, or financial advice.
- Reliable estimates for every Indian city regardless of dataset coverage.
- Live property-portal scraping or an automatically refreshed market feed.
- Property listing creation, booking, payments, chat, broker leads, or marketplace transactions.
- Model training during a user prediction request.
- Public user-uploaded data or model artifacts.
- Multiple separate microservices for every application feature.
- Presenting synthetic records or simulated analytics as real market observations.

### 3.3 Release priorities

- **P0:** required for the first verified local release.
- **P1:** advanced capability planned after core flows work; it may be included in the release only if P0 is stable and tested.
- **P2:** future enhancement requiring separate approval.

---

## 4. System Overview and Service Boundaries

### 4.1 Logical architecture

```text
Browser
  |
  v
Next.js + TypeScript frontend
  | HTTPS/HTTP JSON API (local development may use HTTP)
  v
Django REST Framework application backend
  |-- Authentication, authorization, business rules
  |-- User/profile/prediction/report persistence
  |-- Protected service-to-service HTTP request
  v
Independent Python inference service
  |-- Request schema validation
  |-- Loads reviewed model pipeline artifact
  |-- Runs inference; does not own user records
  v
Versioned scikit-learn pipeline artifact

Offline ML training workflow (separate process/environment)
  -> audit -> clean -> feature engineer -> split -> train -> evaluate
  -> review/promote artifact -> make artifact available to inference service
```

### 4.2 Applications and responsibilities

**Frontend — `frontend/`**
- Next.js with TypeScript.
- Renders pages, forms, chart components, loading/error states, and client-side validation.
- Calls the Django public application API; it shall not call the inference service directly.
- Shall not contain database credentials, service secrets, or the trained model artifact.

**Application backend — `backend/`**
- Python and Django REST Framework.
- Owns authentication, authorization, account/profile data, prediction history, administrator operations, report filtering/export, and public API responses.
- Validates the caller and request before calling the inference service.
- Calls inference through a documented HTTP contract; it shall not import inference-service application code at runtime.

**Inference service — `inference-service/`**
- An independently runnable/deployable Python HTTP service built with **FastAPI** (approved architecture decision).
- Owns model artifact loading and prediction execution only. It shall not own user authentication, account records, or prediction-history storage.
- Shall not train or retrain models in a request path.
- Shall protect internal endpoints using private-network controls and/or service authentication appropriate to the deployment.

**Offline ML workflow — `ml/training/`**
- Owns dataset profiling, cleaning, feature engineering, experiment execution, model training, evaluation, and artifact creation.
- Runs separately from frontend, backend, and inference service startup.
- Publishes a reviewed artifact version; live inference shall not pick up unreviewed experimental artifacts automatically.

**Database**
- SQLite is used for local development.
- PostgreSQL is required for production deployment (enforced via `config.settings.production` with no silent fallback to SQLite).
- The application backend owns database writes. The inference service shall not access the application database directly.

### 4.3 Independence requirements

- Each deployable service shall have separate dependencies, configuration, startup instructions, health/readiness behavior, and tests.
- Service-to-service communication shall use documented HTTP contracts rather than importing another service's application modules.
- The monorepo may contain all applications, but the applications shall be capable of separate startup and deployment.
- Shared schemas/constants must be versioned or copied through a documented contract; a change to a request schema must not silently break another service.
- Docker/Compose is optional for initial development and shall not be required to run the first local version unless explicitly approved.

---

## 5. Actors, Roles, and Main Use Cases

### 5.1 Visitor
- Can view public information, workflow, supported inputs/locations, and limitations.
- Can register or sign in.
- Cannot view private history, user-management records, or administrator reports.

### 5.2 Registered user
- Can register, authenticate, sign out, and manage permitted profile fields.
- Can submit supported property details for an estimate.
- Can view the result of a successful estimate.
- Can view only their own saved prediction history and permitted details.

### 5.3 Administrator
- Must be provisioned through a protected administrative process; public registration shall not grant administrator privileges.
- Can access administrator pages and endpoints after server-side authorization.
- Can view/manage users within approved permissions, view prediction records, filter reports by date, export permitted fields, and view published model information.

### 5.4 ML maintainer/developer
- Runs the offline training workflow, reviews metrics and data-quality reports, and prepares a candidate artifact.
- Must not publish a candidate model automatically without required evaluation and review.
- Production artifact promotion shall be documented and repeatable.

### 5.5 Main use cases

| Use case | Primary actor | Result |
|---|---|---|
| Register and sign in | Visitor | Authenticated user account |
| Submit property details | Registered user | Validated prediction request |
| View estimate | Registered user | Model-generated INR estimate, or a clear error |
| Review history | Registered user | Only the user's own saved predictions |
| Review dashboard/report | Administrator | Actual database-backed statistics and filtered records |
| Train and evaluate model | ML maintainer | Reproducible metrics and candidate artifact |
| Promote model | Authorized maintainer | Versioned artifact available to inference after compatibility checks |

---

## 6. Functional Requirements

Each requirement has a stable ID for mapping to tests and delivery phases. Unless stated otherwise, requirements marked P0 are required before the first local release.

### 6.1 General website requirements

**FR-GEN-001 — Public homepage (P0)**  
The system shall provide a responsive homepage explaining the product, the prediction workflow, the broad data source, and the limitations of estimates.

**Acceptance checks:** Homepage loads without authentication; primary navigation works; no unsupported claim such as “guaranteed price” or fabricated accuracy is displayed.

**FR-GEN-002 — About/how-it-works information (P0)**  
The system shall explain that the estimate is based on a historical listing dataset and a machine-learning model, and that it is not a certified valuation.

**FR-GEN-003 — Supported inputs and locations (P0)**  
The system shall show only input choices approved by the final data/model schema. Supported locations shall come from a normalized, validated source, not an unrelated hard-coded list.

**FR-GEN-004 — Consistent states (P0)**  
Pages that load data or submit requests shall provide understandable loading, success, empty, and error states.

### 6.2 Authentication and profile requirements

**FR-AUTH-001 — Registration (P0)**  
A visitor shall be able to create an ordinary user account using the approved required fields. The backend shall validate the input and reject invalid or duplicate account identifiers according to the final account policy.

**Acceptance checks:** Valid registration creates one account; invalid input does not create an account; repeated registration for a unique identifier returns a clear validation response; the password is never stored or returned in plaintext.

**FR-AUTH-002 — Sign in (P0)**  
A registered user shall be able to authenticate using the selected authentication mechanism. Failed authentication shall not reveal whether a sensitive credential component was correct beyond the documented user-facing message.

**FR-AUTH-003 — Sign out (P0)**  
The system shall invalidate/clear the session or token according to the approved authentication design. A signed-out client shall not be able to reuse protected UI state as proof of authentication.

**FR-AUTH-004 — Current user and profile (P0)**  
An authenticated user shall be able to retrieve and update only permitted profile fields. Role, staff, or administrative permissions shall not be editable through ordinary profile APIs.

**FR-AUTH-005 — Server-side authorization (P0)**  
The backend shall enforce authentication, roles, and record ownership regardless of what the frontend displays or hides.

**FR-AUTH-006 — Administrator provisioning (P0)**  
Public registration shall always create a normal user. Administrator access shall be granted only by a protected management operation or approved deployment/bootstrap process.

**FR-AUTH-007 — Authentication design (Approved; implementation in Phase 4)**
The authentication architecture shall use Django REST Framework with SimpleJWT. The browser pattern shall hold a short-lived access JWT in frontend memory (sent in `Authorization: Bearer <token>`) and receive a refresh token in an `HttpOnly` cookie (`Secure` in production HTTPS, with appropriate `SameSite`, `Domain`, and `Path` attributes). Refresh rotation and logout invalidation shall be enforced, alongside CSRF protection for cookie-backed refresh/logout operations. Tokens shall never be persisted in browser `localStorage` or `sessionStorage`. Authoritative permissions and ownership checks are enforced strictly by the backend. Phase 4 implementation shall explicitly implement and test the custom cookie, CSRF, refresh, and logout handlers.

### 6.3 Property input and prediction requirements

**FR-PRED-001 — Property input form (P0)**  
The frontend shall collect only fields in the approved model feature schema. Planned candidates are location, area value and area basis, BHK, bathrooms, balcony, floor, furnishing, transaction type, ownership, and optional facing. Final availability is conditional on the completed dataset audit.

**FR-PRED-002 — Client and server validation (P0)**  
The client may provide immediate field validation, but the backend and inference service shall validate all security- and model-critical fields independently. Client validation alone shall not be trusted.

**FR-PRED-003 — Area basis and unit (P0)**  
The request and result shall represent area basis/unit unambiguously. Carpet Area and Super Area shall not be treated as interchangeable. The backend shall accept only approved units and conversion rules. Unknown/ambiguous units shall be rejected with a clear error.

**FR-PRED-004 — Supported location (P0)**  
The backend shall validate a location against the normalized supported-location list. Unsupported locations shall receive a defined error and shall not result in a fabricated price. Any future fallback behavior requires documented model validation and product-owner approval.

**FR-PRED-005 — Prediction request (P0)**  
An authenticated user shall be able to submit valid property details. The backend shall verify the request, call the inference service, validate the returned result, and respond with a normalized price and summary.

**FR-PRED-006 — Price format and currency (P0)**  
The API shall represent the predicted price as a numeric INR amount with a documented precision/rounding rule. The frontend shall format the value for Indian readers, including lakh/crore presentation where appropriate. Formatted strings shall not be used as the canonical numeric value in storage or calculations.

**FR-PRED-007 — Save successful prediction (P0)**  
After a valid prediction response is received and validated, the backend shall save the successful prediction with the authenticated user, normalized input snapshot, numeric INR amount, timestamp, model version, and request/correlation identifier where available.

**FR-PRED-008 — No false-success response (P0)**  
If validation fails, inference is unavailable, the artifact is not ready, or the response is invalid, the system shall return a defined error and shall not display or save a fabricated successful price. The system shall not silently substitute zero, a fixed number, or a stale estimate.

**FR-PRED-009 — Prediction disclaimer (P0)**  
The result page shall state that the output is an ML estimate based on listing data and may differ from the final sale price. The result shall not imply a guarantee or certified valuation.

**FR-PRED-010 — Derived price per square foot (P1)**  
If enabled, the backend/frontend shall calculate price per square foot only using a valid, normalized area value and an explicitly identified area basis. The UI shall identify the basis used.

**FR-PRED-011 — Model-supported insights (P1)**  
If feature importance or explanations are displayed, they shall be generated from documented model-analysis methods. The UI shall not claim causal reasons for an individual price unless the method supports that claim.

### 6.4 Prediction history requirements

**FR-HIST-001 — List personal history (P0)**  
An authenticated user shall be able to view a paginated list of their successful saved predictions, newest first by default.

**FR-HIST-002 — Detail view (P0)**  
An authenticated user shall be able to view details of a history entry only if the entry belongs to them or they have explicit administrator permission.

**FR-HIST-003 — Data isolation (P0)**  
Changing an identifier in a URL, query parameter, or request body shall not allow a user to read another user's prediction.

**FR-HIST-004 — Empty history state (P0)**  
A user with no predictions shall see an appropriate empty state, not fabricated entries.

**FR-HIST-005 — Record integrity (P0)**  
A saved prediction shall retain its normalized input snapshot, output amount, creation timestamp, and model-version identifier so the displayed history is traceable to the original result.

### 6.5 Administrator requirements

**FR-ADM-001 — Admin dashboard (P0)**  
Authorized administrators shall be able to view totals and summaries calculated from actual database records, including registered users and saved predictions.

**FR-ADM-002 — User management (P0)**  
Authorized administrators shall be able to view registered users and perform only the user-management actions approved for the release. Sensitive credential data shall never be shown.

**FR-ADM-003 — Prediction records (P0)**  
Authorized administrators shall be able to inspect prediction records with appropriate pagination and filtering. Access to personal information shall be limited to fields required for the approved administrative purpose.

**FR-ADM-004 — Date-range report (P0)**  
An administrator shall be able to filter predictions by a start and end date. The system shall validate date format, inclusive/exclusive boundary behavior, and start-before-end semantics; these details shall be documented in the API contract.

**FR-ADM-005 — Admin-only enforcement (P0)**  
Non-admin users shall receive a defined forbidden/unauthorized response when accessing admin APIs or attempting admin actions, even if they manually construct an HTTP request.

**FR-ADM-006 — Analytics charts (P1)**  
Charts shall be based on actual database aggregates and shall display suitable labels, units, and empty-data states. The system shall not generate dummy statistics to fill gaps.

**FR-ADM-007 — CSV export (P1)**  
Authorized administrators shall be able to export the currently filtered report using an approved allowlist of columns. Passwords, tokens, secret fields, and unapproved personal data shall never be exported. Exported values shall be handled to reduce spreadsheet formula-injection risk.

**FR-ADM-008 — Model information (P0)**  
The administrator shall be able to view the published model version and its actual evaluation metadata. Metrics shall not be hard-coded or described as “accuracy” if they are regression error metrics.

### 6.6 Backend API requirements

**FR-API-001 — Versioned API (P0)**  
Application endpoints shall use a versioned path, proposed as `/api/v1/`. Incompatible changes shall require a versioning decision and updated contract/tests.

**FR-API-002 — JSON contracts (P0)**  
Request and response payloads shall be documented in an OpenAPI specification or equivalent contract file. The frontend shall not rely on undocumented implementation details.

**FR-API-003 — Consistent errors (P0)**  
The API shall return a consistent error shape with a machine-readable code, user-safe message, field errors where relevant, and a correlation/request identifier where available. Internal stack traces and secrets shall not be returned.

**FR-API-004 — Pagination and filtering (P0)**  
History and administrator listing endpoints shall support bounded pagination. Admin report filters shall be validated server-side.

**FR-API-005 — Request limits (P0)**  
Request body size and list/page-size parameters shall be bounded. Suitable throttling/rate limits shall be applied to authentication and expensive prediction endpoints according to local and deployment needs.

**FR-API-006 — Frontend API routing (P0)**  
The frontend shall call the Django application API using an environment-configured base URL. The API URL shall not be hard-coded throughout components.

**FR-API-007 — No frontend-to-inference bypass (P0)**  
The browser shall not call the internal inference service directly. The Django backend shall be the public application boundary and shall make protected server-to-server inference calls.

### 6.7 Inference service requirements

**FR-INF-001 — Independent runtime (P0)**  
The inference service shall start and run independently of Django and Next.js, with its own dependencies, configuration, tests, and documented startup command.

**FR-INF-002 — Model load once (P0)**  
The service shall load and validate the approved model artifact during application startup or controlled initialization, rather than loading/training the model on every prediction request.

**FR-INF-003 — Readiness (P0)**  
The service shall expose health/readiness behavior that distinguishes a live process from a service ready to predict with a compatible artifact.

**FR-INF-004 — Prediction endpoint (P0)**  
The service shall expose a versioned internal prediction endpoint accepting the approved normalized feature schema and returning a numeric INR prediction, model version, and request identifier when available.

**FR-INF-005 — Schema validation (P0)**  
The inference service shall reject missing required fields, unknown categories where strict validation is required, impossible numeric values, incompatible schema versions, and unsupported units with explicit safe errors.

**FR-INF-006 — Protected internal access (P0)**  
Prediction endpoints shall not be anonymously available to the public internet by default. Service-to-service authentication and/or private networking shall be configured before deployment.

**FR-INF-007 — Artifact compatibility (P0)**  
At startup, the service shall verify required artifact files and metadata, model version, expected feature schema, target currency/unit, and compatible dependency information. Incompatible or missing artifacts shall make readiness fail; the service shall not silently use an arbitrary artifact.

**FR-INF-008 — Output sanity checks (P0)**  
The service shall reject non-finite values and apply documented policy to invalid/non-positive model outputs. It shall not silently clip or substitute values without an approved and evaluated policy.

**FR-INF-009 — No training at inference (P0)**  
Inference requests shall only apply an already trained and approved pipeline. They shall not fit encoders, imputers, scalers, or estimators on request data.

### 6.8 Offline ML training requirements

**FR-ML-001 — Reproducible audit (P0)**  
The training workflow shall produce an audit report containing source/version information, raw row/column counts, column types, missingness, unique counts, duplicate counts, target parse results, area-unit findings, location distribution, and data-quality warnings.

**FR-ML-002 — Price target normalization (P0)**  
The workflow shall parse supported price labels such as `Lac` and `Cr` into numeric INR using tested rules. Non-price labels such as `Call for Price` and unparseable values shall be excluded from supervised target training and counted in the report.

**FR-ML-003 — Area normalization policy (P0)**  
The workflow shall document supported area units and conversion factors. It shall distinguish Carpet Area from Super Area, handle missingness explicitly, and reject/omit ambiguous conversions. It shall not infer unknown unit conversions by guessing.

**FR-ML-004 — Duplicate investigation (P0, blocking)**  
The workflow shall compare records excluding the unique `Index` identifier, reproduce the preliminary duplicate findings, distinguish exact duplicates from near-duplicate/similar listings where possible, and document the deduplication policy before creating final train/validation/test data.

**FR-ML-005 — Leakage prevention (P0)**  
`Index` shall not be a predictive feature. `Price (in rupees)` shall be excluded by default until its semantics and target-derived leakage risk are resolved. Raw `Description` shall be excluded from initial features due to potential target leakage. Feature inclusion changes shall be documented and tested.

**FR-ML-006 — Reproducible split (P0)**  
The workflow shall separate training, validation/model selection, and final holdout testing. Duplicate/near-duplicate leakage shall be reviewed before the split. Split strategy, random seed, and data version/fingerprint shall be recorded. If multiple records can represent the same listing/entity, group-aware separation shall be considered and documented.

**FR-ML-007 — Baseline and candidate comparison (P0)**  
The workflow shall compare a simple baseline, such as `DummyRegressor`, against appropriate regression candidates. Initial candidates may include Linear/Ridge Regression, Decision Tree Regressor, Random Forest Regressor, and HistGradientBoosting Regressor. Final model choice shall be based on reproducible validation results and operational suitability.

**FR-ML-008 — Evaluation metrics (P0)**  
The workflow shall report MAE, RMSE, and R² on an untouched holdout test set. It shall provide city/segment results where sample sizes support interpretation, and it shall clearly state limitations and sample coverage. Regression metrics shall not be mislabeled as classification accuracy.

**FR-ML-009 — Baseline improvement target (P0 reporting; target not guaranteed)**  
The workflow shall compare candidate MAE with the baseline MAE. The PRD's proposed target is at least 10% MAE improvement. If the target is not achieved, the report shall state that result and recommend investigation; data/test manipulation to force a pass is prohibited.

**FR-ML-010 — Full fitted pipeline artifact (P0)**  
The workflow shall persist preprocessing and the selected estimator together as a versioned artifact whenever technically feasible, preferably a single scikit-learn pipeline serialized with a trusted format such as joblib. Training and inference transformations shall be demonstrably consistent.

**FR-ML-011 — Metadata and provenance (P0)**  
Each candidate/released model shall have metadata including model version, target name/unit, feature schema/version, dataset version/fingerprint, training timestamp, dependency versions, split strategy, metrics, and known limitations.

**FR-ML-012 — Controlled promotion (P0)**  
A model shall not be considered production-ready until evaluation is reviewed, artifact-load tests pass, and the approved version is explicitly selected. Experimental artifacts shall not automatically replace the live model.

**FR-ML-013 — Training dependency isolation (P0)**  
Training-only dependencies and notebooks shall not be required for the inference service to start, except for explicitly shared runtime dependencies necessary to load the selected model.

### 6.9 Documentation requirements

**FR-DOC-001 (P0)** — Root README shall explain repository layout, prerequisites, services, environment variables, commands, tests, common troubleshooting, and links to detailed documents.

**FR-DOC-002 (P0)** — `DATASET_ML_SPEC.md` or equivalent shall document dataset source/licence status, data dictionary, cleaning rules, supported features, target definition, model evaluation, and limitations.

**FR-DOC-003 (P0)** — `ARCHITECTURE.md` shall document service boundaries, API call flow, database ownership, local ports/configuration, authentication decision, and deployment model.

**FR-DOC-004 (P0)** — `IMPLEMENTATION_PLAN.md` shall map requirements to phases, tests, deliverables, open defects, and explicit approval gates.

**FR-DOC-005 (P0)** — Setup and test commands documented in the README shall be verified in a clean environment before local release.

---

## 7. External Interface Requirements

### 7.1 User interface

- Next.js and TypeScript shall be used for the frontend.
- The interface shall be responsive and support keyboard navigation, visible focus indicators, associated form labels, readable errors, and accessible chart summaries.
- The UI shall distinguish normal-user and administrator navigation while relying on server-side authorization for actual access control.
- INR display shall use Indian number grouping and avoid rounding the stored canonical value in an inconsistent way.
- UI choices shall match the approved schema and normalized location list.

### 7.2 Public application API

Proposed public route contract (exact schemas and authentication details must be documented in `contracts/application-api.yaml` or `contracts/openapi.yaml`):

| Method | Route | Access | Purpose |
|---|---|---|---|
| `POST` | `/api/v1/auth/register/` | Public | Register a normal user |
| `POST` | `/api/v1/auth/login/` | Public | Authenticate |
| `POST` | `/api/v1/auth/logout/` | Authenticated | End authenticated session/token lifecycle |
| `GET` | `/api/v1/auth/me/` | Authenticated | Get current user's safe profile |
| `PATCH` | `/api/v1/auth/me/` | Authenticated | Update permitted profile fields |
| `GET` | `/api/v1/locations/` | Public or authenticated, as decided | Get supported location choices and metadata |
| `POST` | `/api/v1/predictions/` | Authenticated | Validate, request inference, persist successful prediction, return result |
| `GET` | `/api/v1/predictions/` | Authenticated | List current user's history; admin filters separately authorized |
| `GET` | `/api/v1/predictions/{id}/` | Owner or authorized admin | Get one history item |
| `GET` | `/api/v1/admin/summary/` | Admin | Real database-backed summary |
| `GET` | `/api/v1/admin/users/` | Admin | Paginated user management list |
| `GET` | `/api/v1/admin/predictions/` | Admin | Filtered prediction records |
| `GET` | `/api/v1/admin/reports/` | Admin | Date-filtered report data |
| `GET` | `/api/v1/admin/reports/export/` | Admin, P1 | CSV export of approved columns |
| `GET` | `/api/v1/model/metrics/` | Read-only access policy to be set | Published model metadata/metrics only |

The exact route names may be refined during architecture design, but any change shall update the contract, traceability table, and tests before it is considered complete.

### 7.3 Inference service API

Proposed internal contract, not publicly accessible by default:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/health/live` | Process liveness |
| `GET` | `/health/ready` | Artifact compatibility and prediction readiness |
| `POST` | `/api/v1/predict` | Predict a listing price for a validated schema |
| `GET` | `/api/v1/model/metadata` | Return permitted metadata for the loaded model version |

### 7.4 Prediction request/response contract (provisional)

The exact feature list will be frozen after Phase 1's dataset audit. A conceptual request may resemble:

```json
{
  "schema_version": "1.0",
  "location": "approved-normalized-location",
  "area_value": 1000,
  "area_basis": "CARPET",
  "bhk": 2,
  "bathrooms": 2,
  "balcony": 1,
  "floor_number": 3,
  "total_floors": 12,
  "furnishing": "SEMI_FURNISHED",
  "transaction_type": "RESALE",
  "ownership": "FREEHOLD",
  "facing": null
}
```

This is an example schema only, not a final commitment that every field exists or is reliable in the uploaded dataset. The final contract shall define required/optional fields, enums, ranges, units, nullability, and normalization rules.

Successful public response concept:

```json
{
  "prediction_id": "server-generated-id",
  "estimated_price_inr": 4200000.0,
  "currency": "INR",
  "model_version": "approved-version-id",
  "created_at": "ISO-8601 timestamp",
  "property_summary": {
    "location": "approved-normalized-location",
    "area_value": 1000,
    "area_unit": "sqft",
    "area_basis": "CARPET"
  },
  "disclaimer": "This is a model estimate based on historical listing data, not a guaranteed sale price."
}
```

The example amount is illustrative only, not a real model output or a claim about a property's value. The final API contract shall use a documented numeric precision and timestamp/time-zone rule.

### 7.5 Error response format (provisional)

The application APIs shall use a consistent shape similar to:

```json
{
  "error": {
    "code": "UNSUPPORTED_LOCATION",
    "message": "This location is not currently supported.",
    "fields": {},
    "request_id": "correlation-id"
  }
}
```

Exact HTTP status codes and error codes must be enumerated in the API contract. Client-safe messages may be shown to users; stack traces and internal implementation details must not be exposed.

### 7.6 Service-to-service interface

- Django shall authenticate to inference using the approved service credential/private-network approach.
- The request shall include a schema version or equivalent contract version.
- Calls shall have a configured timeout and defined retry policy. Automatic retries must not cause duplicate user-history records or uncontrolled expensive inference.
- Django shall validate the response schema, price value, model version, and request/correlation identifier before storing a successful prediction.
- If inference is unavailable or returns invalid data, Django shall return a safe error; it shall not fabricate a price.

### 7.7 Database interface

The application backend shall access the application database via Django ORM. The inference service shall not use that database. Initial local development may use SQLite; production database choice and migrations shall be finalized before deployment.

### 7.8 Artifact interface

- The training process shall write a versioned fitted pipeline artifact and metadata.
- The inference service shall load only the configured approved artifact.
- Artifact location shall be configurable and shall not be assumed to be a writable directory in a read-only production image.
- Model files shall not be uploaded by ordinary users.
- `joblib`/pickle-based artifacts shall only be loaded from trusted, reviewed sources.

---

## 8. Data Requirements

### 8.1 Preliminary uploaded dataset audit

The supplied `house_prices.csv` was inspected and produced the following preliminary figures. These figures must be reproduced by the Phase 1 audit command and recorded in `DATASET_ML_SPEC.md` before model training begins.

| Observation | Preliminary result |
|---|---:|
| Rows | 187,531 |
| Columns | 21 |
| Distinct raw `location` values | 81 |
| `Amount(in rupees)` values parsed by a simple Lac/Cr parser | 177,847 |
| `Call for Price` records | 9,684 |
| Missing `Carpet Area` | 80,673 |
| Missing `Super Area` | 107,685 |
| Missing `Price (in rupees)` | 17,665 |
| Missing `Car Parking` | 103,357 |
| Missing `facing` | 70,233 |
| Missing `overlooking` | 81,436 |
| Missing `Society` | 109,678 |
| Entirely empty columns | `Dimensions`, `Plot Area` |
| Duplicate occurrences after dropping `Index` | 119,339 |
| Unique row combinations after dropping `Index` | 68,192 |

Interpretation constraints:
- `Index` is a record identifier and shall not be used as a predictive feature.
- Raw location labels are not necessarily verified city names; normalize spelling/case/aliases and document mappings.
- The simple parser count is a preliminary observation; the production cleaning parser must handle whitespace, number formats, unexpected labels, and invalid values with tests.
- Duplicate statistics need a documented policy. Repeated identical feature rows may represent repeated scraped listings; removal must be deliberate and reported.

### 8.2 Canonical application entities

The following logical entities are required; exact field types and migrations shall be detailed in `ARCHITECTURE.md` and implementation tasks.

**User/account**
- Unique account identifier(s) according to chosen authentication policy.
- Password handled via framework-provided secure hashing.
- Active/suspended state and role/permissions.
- Created/updated timestamps where useful.
- No plaintext password or secret token fields exposed by APIs.

**User profile**
- User relationship and permitted profile fields.
- Profile edit rights limited to allowed fields.

**Prediction record**
- Server-generated identifier.
- User foreign key.
- Validated, normalized input snapshot and input schema version.
- Numeric estimated price in INR using an appropriate decimal/precision strategy.
- Currency identifier `INR`.
- Model version identifier.
- Created timestamp with timezone behavior documented.
- Request/correlation ID where available.
- Optional status/error metadata only if deliberately designed; failed requests shall not be represented as successful predictions.

**Model metadata**
- Model version, artifact identifier/checksum, feature schema version, target unit/currency, dataset fingerprint/version, training date, dependency versions, evaluation metrics, and limitations.

### 8.3 Data ownership and access

- The application backend owns user, profile, prediction, and report data.
- A normal user may access only their own private records.
- Admin access shall be restricted by role and least privilege.
- CSV exports shall include only approved fields.
- Dataset raw files and model artifacts shall have their own provenance and access controls; they are not ordinary user records.

### 8.4 Retention and deletion (decision required before production)

Before online deployment, define the retention period for account and prediction records, what happens when an account is deactivated/deleted, backup retention, and whether users can request deletion/export. This policy shall be reflected in user-facing privacy information and implemented consistently.

---

## 9. Machine-Learning Requirements and Controls

### 9.1 Target definition

The target is the cleaned numeric value represented by `Amount(in rupees)`, subject to verification that the field consistently represents a listing/asking price. The project must not claim that the target is an actual closing transaction price unless the source proves that semantics.

### 9.2 Candidate input features

Candidate fields, pending the actual audit:
- normalized `location`;
- normalized property area and explicit area basis;
- BHK extracted from `Title` when parseable and validated;
- `Bathroom` and `Balcony` if sufficiently usable;
- structured floor information parsed from `Floor`;
- `Furnishing`, `Transaction`, and `Ownership` where categories are reliable;
- `facing` if missingness/quality and model validation justify its inclusion.

Do not automatically include all candidate fields. The final feature list shall be documented with inclusion/exclusion rationale, missingness, expected availability at prediction time, and the form/API mapping.

### 9.3 Leakage prevention

- Raw `Description` is excluded from the first model because it may contain price or target-revealing information.
- `Price (in rupees)` is excluded unless a documented audit establishes a safe meaning and no target leakage; default is exclusion.
- `Index` is excluded.
- Preprocessing, imputation, encoding, feature selection, and scaling (where needed) shall be fit on training data only.
- No test-set result may guide model selection unless a fresh untouched test set is subsequently used.

### 9.4 Splitting and validation

- The split strategy shall be chosen after duplicate and near-duplicate audit.
- A reproducible train/validation/test split is required. The final test set shall not be used during fitting or tuning.
- Split seed, row counts, grouping rules, and source fingerprint shall be recorded.
- When feasible and meaningful, add a location/segment evaluation to expose uneven performance; do not present results for tiny segments as reliable.
- If the dataset structure indicates related/near-identical listing groups, a group-aware split shall be used or the reason for not using it documented.

### 9.5 Candidate models and evaluation

The training workflow shall compare a `DummyRegressor` baseline with suitable regression candidates. Initial candidates include Linear/Ridge Regression, Decision Tree Regressor, Random Forest Regressor, and HistGradientBoosting Regressor. The final set may change based on data, runtime, and evaluation evidence.

Required metrics:
- MAE in INR (and optionally displayed in lakh for readability, with clear units).
- RMSE in INR.
- R² score.
- Baseline comparison.
- Segment/city errors where sample counts support meaningful interpretation.

A proposed goal is at least 10% lower MAE than the baseline. Failure to reach that goal triggers investigation and honest reporting; it must not lead to data leakage or test manipulation.

### 9.6 Artifact and reproducibility

- Save the fitted preprocessing and estimator together as one versioned inference pipeline where feasible.
- Store a metadata manifest containing feature schema, target unit, source dataset fingerprint/version, training run identifier, library versions, metrics, and known limitations.
- Pin compatible runtime dependencies for inference. Training may have additional packages not required by the production service.
- Test a saved-and-reloaded artifact against known test records within documented numeric tolerance.
- Verify the artifact source and checksum before deployment where practical.
- Model promotion shall be explicit and reversible; retain a way to identify the previous approved version.

### 9.7 Inference monitoring (first release minimum)

- Record model version and non-sensitive operational metadata with predictions.
- Track inference errors, latency, and artifact-readiness failures without logging secrets or unnecessary property-owner personal data.
- Do not silently retrain in production. Model refresh requires a new offline evaluation and promotion step.

---

## 10. Non-Functional Requirements

### 10.1 Maintainability and modularity

**NFR-MOD-001:** Frontend, application backend, inference service, and offline training shall have separate dependencies and startup/test instructions.  
**NFR-MOD-002:** Runtime communication between deployable services shall use documented HTTP contracts rather than direct imports of another service's application code.  
**NFR-MOD-003:** Source code shall use clear modules, typed request/response schemas where supported, configuration through environment variables, and avoid duplicated preprocessing logic.  
**NFR-MOD-004:** Important architectural choices and deviations shall be documented.

### 10.2 Reliability and error handling

**NFR-REL-001:** The application shall handle invalid user input, unavailable inference service, missing/incompatible artifacts, and database failures without exposing internals or fabricating results.  
**NFR-REL-002:** Service readiness shall reflect whether required configuration/artifacts are available.  
**NFR-REL-003:** Timeouts shall exist for service-to-service calls; retry behavior shall be bounded and shall not create duplicate successful prediction records.  
**NFR-REL-004:** Database schema changes shall be captured in migrations and applied through documented commands.

### 10.3 Performance

**NFR-PERF-001:** Interactive pages and API routes shall avoid unnecessary full-dataset loads or unbounded queries.  
**NFR-PERF-002:** History/report endpoints shall be paginated and database queries shall be filtered/indexed where needed.  
**NFR-PERF-003:** Model inference shall use a loaded pipeline and shall not train at request time.  
**NFR-PERF-004:** During Phase 6, define and measure local response-time targets on documented hardware and a representative dataset. If a numeric target is adopted, record test conditions and percentile; do not report an unmeasured target as achieved.

### 10.4 Security and privacy

**NFR-SEC-001:** Passwords shall be handled through framework-supported secure hashing and shall never be logged or returned.  
**NFR-SEC-002:** Authorization checks shall run on the server for every protected action and object.  
**NFR-SEC-003:** Secrets and environment-specific credentials shall not be committed to source control or exposed in client bundles.  
**NFR-SEC-004:** Production traffic shall use HTTPS. CORS shall allow only configured frontend origins. CSRF protections shall be used when required by the selected cookie/session design.  
**NFR-SEC-005:** Inference service access shall be protected from unauthenticated public access by service authentication and/or private networking.  
**NFR-SEC-006:** User input shall be validated and safely rendered; CSV exports shall reduce formula-injection risk.  
**NFR-SEC-007:** Model artifacts shall only be loaded from trusted, reviewed sources because serialized Python objects can execute unsafe behavior.  
**NFR-SEC-008:** Logs and error responses shall exclude passwords, tokens, production secrets, and unnecessary personal data.

### 10.5 Usability and accessibility

**NFR-UX-001:** Layouts shall support mobile, tablet, and desktop screen sizes.  
**NFR-UX-002:** Forms shall have visible labels, keyboard-accessible controls, field-level validation messages, and visible focus indicators.  
**NFR-UX-003:** Important status shall not be indicated by color alone.  
**NFR-UX-004:** Charts shall provide text labels/summary so key information is not available only visually.  
**NFR-UX-005:** Price and area units shall be explicitly labelled.

### 10.6 Compatibility and reproducibility

**NFR-COMP-001:** Dependency versions shall be pinned/locked per service in a documented, reproducible manner.  
**NFR-COMP-002:** Node.js, Python, and package versions shall be chosen for mutual compatibility and recorded before implementation starts.  
**NFR-COMP-003:** A clean local setup following the README shall not depend on undocumented files from the developer's machine.  
**NFR-COMP-004:** Tests shall be runnable per service and as a documented integrated suite.

### 10.7 Observability

**NFR-OBS-001:** Services shall emit useful structured logs for startup, readiness, request failures, and inference errors.  
**NFR-OBS-002:** Use a correlation/request identifier across frontend-visible API errors, Django logs, and inference calls where practical.  
**NFR-OBS-003:** Do not log full request payloads by default if they may contain personal or sensitive information.

### 10.8 Deployment and operations

**NFR-DEP-001:** Local development shall work without online deployment or a container runtime unless explicitly approved.  
**NFR-DEP-002:** Production config shall be environment-specific and secrets supplied through the hosting platform's secret mechanism.  
**NFR-DEP-003:** Production database persistence, migrations, backup/retention policy, HTTPS, allowed origins, and health checks shall be verified before launch.  
**NFR-DEP-004:** Frontend, backend, and inference service shall be independently deployable.  
**NFR-DEP-005:** Deployment shall include a smoke test for sign-in, prediction, history persistence, and service failure handling.

---

## 11. Proposed Data Validation Rules

These rules are requirements in principle; exact numeric limits and enums must be finalized from the audited dataset and added to `DATASET_ML_SPEC.md`/API contract before implementation.

- Required fields shall be present, parseable, and consistent with the approved schema.
- Numeric counts such as BHK, bathrooms, and balconies shall reject negative values, impossible formats, and values outside approved bounds.
- Area shall be positive, finite, carry an approved unit/basis, and be convertible through a verified rule.
- Location and categorical values shall match normalized approved categories or be rejected.
- Floor parsing shall distinguish unknown formats from valid floor/total-floor data. Unknown values shall not be silently converted to zero.
- Missing optional values shall follow the documented training/inference policy. The API shall not impute a category differently from the model pipeline.
- Price parser failures shall be counted and reported in training. They shall not turn into zero-valued targets.
- Extreme values shall be audited. Any filtering/winsorization policy must be documented and fitted/selected without looking at the final test outcomes.
- Predictions shall be finite numeric INR values. Invalid or unsupported results shall become errors, not successful responses.

---

## 12. Error Handling Requirements

Exact API status codes and error code catalogue shall be documented in the API contract. The minimum error categories are:

| Category | Example | Required behavior |
|---|---|---|
| Request validation | Missing area, unsupported enum | Return field-level validation error; do not call model when request cannot be normalized |
| Authentication | Missing/invalid credentials | Return safe authentication error; do not reveal secrets |
| Authorization | User requests another user's record | Deny access; do not reveal private record contents |
| Unsupported location/schema | Location not approved or schema version mismatch | Return clear unsupported-input error; do not fabricate an estimate |
| Inference unavailable | Timeout/service unreachable | Return a controlled service error; do not save a successful prediction |
| Model not ready | Missing/incompatible artifact | Readiness fails; prediction endpoint returns controlled unavailable error |
| Invalid model output | NaN/Infinity or policy-invalid price | Reject result, log safe diagnostic context, return controlled error |
| Database failure | History cannot be persisted | Do not claim successful saved history; return controlled error and correlate logs |
| Report/export error | Invalid date range or query failure | Return validation/server error safely, without leaking SQL or filesystem details |

---

## 13. Testing Requirements and Acceptance Criteria

### 13.1 Test levels

**Unit tests** shall cover pure data parsers, feature extraction, validation, service functions, permissions helpers, and UI components where relevant.

**ML tests** shall cover price normalization, area-unit conversions, duplicate audit behavior, leakage exclusions, train/test separation, artifact save/load, predictions on representative rows, finite outputs, and metric calculation.

**Service/API tests** shall cover authentication, role enforcement, ownership, schema validation, inference timeout/unavailable behavior, request/response contract, pagination, date filters, and export allowlists.

**Frontend tests** shall cover form validation, loading/success/error/empty states, navigation, accessible labels, and rendering of INR results.

**End-to-end tests** shall cover registration/login -> submit valid property -> receive estimate -> saved history -> view history, plus a negative test for unauthorized record access and an administrator report flow.

**Deployment smoke tests** shall cover startup/readiness for each service, configuration, database migrations, authentication, a prediction request, persistence, and controlled behavior when inference is unavailable.

### 13.2 Mandatory ML acceptance checks

- The data audit reproduces raw row/column counts, missingness, location values, target parsing, and duplicate findings from the supplied data version.
- The duplicate policy is approved and applied before split creation.
- The target's currency and semantics are documented.
- Candidate models are compared with a baseline on the same valid split protocol.
- MAE, RMSE, and R² are calculated on the untouched holdout test set and reported with units.
- The selected artifact can be loaded by the inference service with matching metadata and schema.
- A deterministic smoke-test input returns a finite result, subject to documented model/numeric tolerance.
- Failure cases do not result in a fabricated successful price.

### 13.3 Mandatory product acceptance checks

- Visitor can view public information and register.
- User can sign in/out and update permitted profile details.
- User can submit valid supported property inputs and receive an INR estimate.
- Invalid/unsupported inputs receive understandable errors.
- Successful prediction is saved with model version and normalized input information.
- User can view their own history; another user's history remains inaccessible.
- Admin-only endpoints reject a normal user.
- Admin summaries and date reports are based on actual database data.
- Frontend cannot bypass Django and call the internal inference endpoint as a public user.
- Frontend, backend, and inference can be started/tested independently.
- Main integrated tests pass in a clean local setup.
- README setup instructions and tested commands are reproducible.

### 13.4 Regression and bug handling

- Every fixed P0 bug shall have a regression test where feasible.
- Critical security, data leakage, prediction corruption, or privacy defects block phase completion.
- Remaining non-blocking defects shall be documented with impact, workaround, and owner before approval.
- A phase is not accepted solely because the UI looks correct; tests and evidence are required.

---

## 14. Phase-Based Requirement Allocation

This table links SRS requirements to the planned phases. Detailed tickets/tasks and evidence belong in `IMPLEMENTATION_PLAN.md`.

| Phase | Focus | Requirement groups | Expected evidence / exit gate |
|---|---|---|---|
| Phase 0 | PRD/SRS/architecture approval | Document decisions, open questions, architecture boundaries | Product owner approves scope; blocking decisions for upcoming work resolved or explicitly accepted |
| Phase 1 | Dataset audit and preparation | FR-ML-001 to FR-ML-006, data requirements | Reproducible audit, approved duplicate and area policies, data dictionary, provenance/licence status |
| Phase 2 | Offline model training and evaluation | FR-ML-007 to FR-ML-013 | Metrics report, baseline comparison, versioned candidate artifact, metadata, save/load test |
| Phase 3 | Independent inference service | FR-INF-001 to FR-INF-009 | Service starts independently, readiness works, contract/validation/artifact tests pass |
| Phase 4 | Django application backend | FR-AUTH, FR-HIST, FR-ADM, FR-API as applicable | Database migrations, authentication/permissions/API tests pass |
| Phase 5 | Next.js frontend | FR-GEN, frontend portions of FR-PRED/FR-HIST/FR-ADM | Core page flows and frontend tests work against actual API contract |
| Phase 6 | Integration and quality | All P0 cross-service requirements and NFRs | End-to-end, security, contract, regression, and failure-mode tests pass |
| Phase 7 | Local release | FR-DOC, setup and release requirements | Fresh local setup and documented test suite verified; owner approves local release |
| Phase 8 | Online deployment | NFR-SEC, NFR-DEP, retention/privacy decisions | Production configuration and smoke tests pass; owner approves deployment |

### 14.1 Phase gate policy

A phase deliverable must include:
1. Summary of completed requirements and changed files.
2. Exact commands run and their outcomes.
3. Test results (pass/fail and skipped tests with reasons).
4. Known defects, risks, and deferred items.
5. Evidence for the exit criteria.
6. Explicit product-owner review/approval before starting the next phase.

The developer/agent shall not start the next phase without that approval, even if future phases are described in the roadmap.

---

## 15. Requirements Traceability

The implementation plan and tests shall maintain a traceability map linking each requirement ID to its implementation component, tests, status, and phase. Minimum traceability examples:

| Requirement ID | Component(s) | Required verification | Phase |
|---|---|---|---|
| FR-AUTH-001 | `backend/apps/accounts/`, `frontend/` auth pages | Registration tests, duplicate/invalid input tests | 4, 5 |
| FR-PRED-003 | Frontend form, Django serializer, inference schema, ML preprocessing | Area-unit contract tests and conversion tests | 1, 3, 4, 5 |
| FR-PRED-008 | Django prediction service + inference client | Timeout, unavailable-service, invalid-output tests | 3, 4, 6 |
| FR-HIST-003 | Django prediction API and permissions | Cross-user access denial tests | 4, 6 |
| FR-ADM-005 | Backend admin permissions | Non-admin direct API request tests | 4, 6 |
| FR-ML-004 | `ml/training/` audit scripts | Duplicate audit reproducibility test/report | 1 |
| FR-ML-008 | `ml/training/` evaluation code | Metric tests and holdout report | 2 |
| FR-INF-007 | Inference artifact loader | Missing/incompatible artifact readiness tests | 3 |
| NFR-SEC-003 | All services and repository configuration | Secret scan/repository review | 6, 7 |
| NFR-DEP-004 | Service configurations | Independent startup/deployment checks | 6, 8 |

No requirement shall be marked complete without linked evidence or a documented, approved exception.

---

## 16. Approved Architecture Decisions & Remaining Open Issues

### 16.1 Approved Architecture Decisions (Phase 0)
1. **Inference framework:** **FastAPI** is approved for `inference-service/`.
2. **Authentication approach:** **Django REST Framework with SimpleJWT** is approved (in-memory access JWT + HttpOnly refresh cookie, rotation/revocation, backend authoritative permissions; implementation in Phase 4).
3. **Database strategy:** **SQLite** is approved for local development; **PostgreSQL** is approved and strictly required for production deployment (enforced in `config.settings.production` with no fallback to SQLite).
4. **Supported runtime versions:** Pinned and verified: Next.js 16.4.2 (Active LTS), React 19.0.0, Django 5.2.18 LTS, DRF 3.18.3, SimpleJWT 5.5.1, FastAPI 0.115.14, Python 3.13.

### 16.2 Remaining Open Issues (Pending Evidence or Relevant Future Phases)
1. **Dataset provenance and licence:** verify the original source, applicable licence, attribution, redistribution rights, and whether the raw CSV can be included in a repository or release package.
2. **Duplicate policy:** reproduce the finding of 119,339 duplicate occurrences after excluding `Index`, investigate row repetition, and approve how exact/near duplicates affect training and evaluation.
3. **Area strategy:** finalize area basis, supported units, conversion table, missing-value strategy, and how Carpet Area versus Super Area is represented in the form.
4. **Final feature schema:** confirm which proposed fields are reliable enough for the model and exposed in the UI.
5. **Location policy:** confirm normalization/aliases, rare categories, minimum sample policy, and unsupported-location behavior.
6. **Privacy/retention/export:** document record-retention, account deletion/deactivation behavior, allowed CSV fields, and privacy notice before production.
7. **Model target/benchmark:** verify `Amount(in rupees)` semantics and reassess the proposed baseline-improvement target after a valid baseline run.

These are not reasons to guess silently. Each open item shall have a recorded decision, owner, and date before the dependent development work starts.

---

## 17. Definition of Done

A feature is done only when all applicable statements are true:

- Its requirement ID is implemented as specified or has an approved deviation.
- Backend-enforced validation and permissions exist where relevant; UI-only restrictions are insufficient.
- Unit/integration/contract tests for the feature pass.
- Loading, empty, success, and error states are implemented as applicable.
- Logs are helpful and do not expose secrets or unnecessary personal data.
- API and documentation contracts are updated.
- No critical or high-severity defect remains open for the feature.
- The changed feature passes regression tests for previously working behavior.
- The phase's evidence and product-owner approval are recorded before progression.

The overall local release is done only when all P0 requirements pass, dataset/model results and limitations are documented, a clean setup is reproducible, and the product owner approves the release. The online release is a separate gate and must pass production smoke and security checks.

---

## 18. Change Control

- Changes to product goals, scope, roles, or major user-visible features shall update `PRD.md` first.
- Exact behavior, validation, error, security, or API changes shall update this SRS and the API contract.
- Changes to service boundaries, runtime decisions, dependencies, or deployment shape shall update `ARCHITECTURE.md`.
- Changes to data-cleaning, features, splits, metrics, or model artifact policy shall update `DATASET_ML_SPEC.md`.
- Every meaningful change shall identify affected requirement IDs and tests.
- Scope expansion during a phase shall require explicit approval and an updated phase plan; unrelated future-phase work shall not be added silently.

---

## 19. Approval Record

| Item | Status |
|---|---|
| SRS version | 1.0 — Review Draft |
| Product owner approval | Pending |
| Blocking decisions reviewed | Pending |
| Architecture decision record linked | Pending |
| Implementation authorization | Not granted by this document alone |

**Implementation may begin only after the product owner approves the relevant requirements and the phase plan.** Approval of this SRS does not imply that any code, model, endpoint, test, or deployment already exists or works.
