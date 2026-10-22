# Product Requirements Document (PRD)

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Product | Real Estate Price Prediction Platform |
| Document | Product Requirements Document (PRD) |
| Version | 1.0 — Final Review Draft |
| Status | Ready for product-owner review and sign-off |
| Prepared on | 22 October 2026 |
| Primary audience | Product owner, developers, ML engineer, tester, project evaluator |
| Primary purpose | College submission and a strong software/ML portfolio project |
| Delivery approach | Local-first development, verified local release, then online deployment |

> **Status note:** This document is a finalized PRD draft for review; it is not evidence that implementation has started or passed tests. The user has requested that work proceed in phases. No application code or implementation ZIP is part of this PRD. Unresolved decisions are listed in Section 16 and must be addressed before the affected phase begins.

---

## 1. Executive Summary

The Real Estate Price Prediction Platform is a web application that estimates residential property **listing prices** in Indian Rupees (INR) from supported property details. It is intended to demonstrate a complete, maintainable product: an interactive web frontend, a secure application backend, a separately deployable machine-learning inference service, an offline model-training workflow, data persistence, reporting, testing, and eventual online deployment.

The product will have two main user roles:

- **Registered user:** creates an account, enters supported property details, receives an estimated price, reviews previous predictions, and manages allowed profile information.
- **Administrator:** reviews operational summaries, manages user access, inspects prediction records, filters reports by date, exports authorized reports, and views published model information.

The agreed architecture is **Next.js + TypeScript for the frontend**, **Python + Django REST Framework for the application backend**, a **separate Python inference service**, and an independent offline ML-training workflow using scikit-learn. SQLite is planned for early local development; PostgreSQL is the preferred production database option, subject to hosting and persistence requirements.

The project will be delivered in controlled phases. Each phase must be tested and reviewed before the next phase starts. Price predictions are model estimates based on listing data, not guaranteed sale prices or certified valuations.

## 2. Background and Product Context

The supplied reference document, *Real Estate Price Prediction Using Python and ML*, describes a system with property inputs, price prediction, user registration/login, profile management, prediction history, an administrator dashboard, registered-user management, prediction records, date-range reports, and role-based admin access.

The reference document originally proposes a Django-rendered web interface. During planning, the frontend and service boundaries were changed to meet the product owner's requirement for a modern frontend and future independent deployment:

- Frontend: Next.js with TypeScript.
- Application backend: Python with Django REST Framework.
- Production inference: an independently runnable/deployable Python service.
- Training: offline and separate from live user requests.
- Local database: SQLite initially.
- Production database: PostgreSQL is preferred, subject to the final hosting decision.

The original user/admin capabilities remain relevant. Detailed software behavior, endpoint contracts, database schema, and test cases will be specified in the SRS and architecture documentation rather than duplicated in full in this PRD.

## 3. Problem, Vision, and Product Principles

### 3.1 Problem

People exploring residential property may want an initial price estimate before undertaking more detailed research. This platform will produce a data-driven estimate from a documented dataset of Indian property listings and provide a usable interface for exploring the estimate and reviewing earlier predictions.

### 3.2 Vision

Deliver a polished and reproducible college/portfolio project that demonstrates how a modern web application and a machine-learning model can work together through well-defined, independently deployable services.

### 3.3 Product principles

1. **Honest estimates:** describe the output as a listing-price estimate, not a guaranteed transaction value.
2. **Evidence over claims:** publish measured model metrics and known limitations; never invent accuracy figures or dashboard statistics.
3. **Data quality first:** verify data provenance, deduplicate appropriately, normalize price/area units, and document cleaning choices before accepting model results.
4. **Modular by design:** frontend, application backend, inference service, and offline training have clear boundaries.
5. **Security by default:** protected actions require server-side authentication and authorization; users cannot access other users' private records.
6. **Phase-gated delivery:** finish and test each phase before moving to the next.
7. **Portfolio-quality delivery:** provide clear setup instructions, architecture and ML documentation, tests, and reproducible results.

## 4. Goals and Success Measures

### 4.1 Product goals

- Provide a responsive interface for estimating supported residential property listing prices in INR.
- Support secure user accounts, profiles, prediction history, and administrator workflows.
- Use a documented and evaluated regression model rather than hard-coded or synthetic live predictions.
- Show user-friendly results and clear estimation limitations.
- Provide actual database-backed administrator summaries and date-filtered reports.
- Keep the frontend, application backend, and inference service independently runnable and deployable.
- Reproduce the local setup and demonstrate a verified path to online deployment.

### 4.2 Success measures

| Area | Success measure |
|---|---|
| Product functionality | All approved P0 requirements and their SRS acceptance tests pass. |
| ML quality | MAE, RMSE, and R² are reported on a held-out test set and compared with a baseline. |
| Baseline comparison | A proposed goal is at least 10% lower MAE than a `DummyRegressor` baseline. If not achieved, investigate and document results; do not distort evaluation or claim success. |
| Data integrity | Data cleaning, duplicate policy, units, feature schema, and dataset provenance are documented and reproducible. |
| Service separation | The frontend communicates with Django over HTTP, and Django communicates with inference over HTTP. No runtime dependency on importing another deployable service's application code. |
| Privacy/security | Automated tests demonstrate that ordinary users cannot access another user's history or administrator-only capabilities. |
| Reproducibility | A clean local environment can follow the documented setup and run the required tests without undocumented files or credentials. |
| Deployment readiness | Deployed smoke tests verify authentication, prediction, database persistence, and the inference-service call. |

The 10% MAE improvement is a **proposed project target**, not current measured performance. The actual metrics will only be available after the data and models have been evaluated.

## 5. Target Users and Roles

### 5.1 Visitor

- Learn what the platform does, how estimates are generated, which inputs/locations are supported, and what limitations apply.
- Register or sign in.
- Cannot access private prediction history or protected admin records.

### 5.2 Registered user

- Register, sign in, sign out, and update permitted profile information.
- Submit supported property details for a price estimate.
- View the estimate and a summary of the submitted property details.
- View only their own saved prediction history.

### 5.3 Administrator

- Access the administrator interface after server-side role verification.
- View real database-backed totals and summaries.
- View/manage registered users within approved permissions.
- Review prediction records and filter reports by date range.
- Export authorized reports to CSV.
- View the latest published model's actual metadata and evaluation results.
- Manage their permitted profile information.

## 6. Scope

### 6.1 In scope — First release (P0)

- Responsive homepage and clear project/limitations information.
- User registration, login, logout, and profile management.
- Property prediction form based only on the approved feature schema.
- INR prediction result with a normalized property summary and disclaimer.
- Authenticated prediction history and user data isolation.
- Administrator dashboard, user management, prediction records, and date-filtered reports.
- Independently runnable frontend, application backend, and inference service.
- Offline dataset audit, preprocessing, model comparison, model evaluation, and versioned model packaging.
- Automated tests, setup documentation, and local release verification.

### 6.2 In scope — Advanced capabilities (P1)

- Interactive analytics charts for prediction trends and price/location distributions where the available data supports them.
- Authorized CSV export of filtered administrator reports.
- Derived price-per-square-foot display when area definition and normalized area are valid.
- Model-supported explanation, such as global feature importance, presented carefully and not as proof of causation for an individual prediction.
- A documented process for promoting a reviewed model version.
- Optional Docker Compose support to simplify local multi-service startup, if needed after the initial setup works.

### 6.3 Out of scope for the first release

- Guaranteed market valuations, legal valuations, bank-approved valuations, or guaranteed resale prices.
- Claims of reliable prediction for every Indian city or property category regardless of dataset coverage.
- Live property-portal scraping or a continuously refreshed commercial data feed.
- Payments, property booking, broker leads, chat, or a real-estate marketplace.
- Retraining the model on each prediction request.
- Allowing ordinary users to upload models or training datasets.
- A separate microservice for every application feature; only the frontend, application backend, and inference service are planned as separately deployable units.
- Synthetic data presented as genuine property-market observations.

## 7. Core Product Requirements

Priorities: **P0** = required for the first working release; **P1** = advanced capability; **P2** = future consideration.

| ID | Priority | Product requirement | Expected outcome |
|---|---|---|---|
| PR-001 | P0 | Public product information | Visitors understand the product, workflow, supported inputs, and limitations. |
| PR-002 | P0 | Account management | Users can register, sign in/out, and manage permitted profile information securely. |
| PR-003 | P0 | Property input | The user can submit valid property details supported by the approved dataset/model schema. |
| PR-004 | P0 | Price estimate | The user receives a model-generated INR estimate with input summary and disclaimer. |
| PR-005 | P0 | Prediction history | A signed-in user can review their own previous predictions. |
| PR-006 | P0 | Administrator operations | Administrators can view/manage users and inspect prediction records according to approved permissions. |
| PR-007 | P0 | Date-filtered reporting | An administrator can view prediction records within a selected date range. |
| PR-008 | P0 | Model transparency | The product shows current supported locations and published model evaluation information where appropriate. |
| PR-009 | P0 | Independent services | The frontend, application backend, inference service, and offline training workflow have clear responsibilities and can be run/tested separately. |
| PR-010 | P0 | Safe failure behavior | Invalid inputs or an unavailable inference service result in a clear error; the application never fabricates a price. |
| PR-011 | P1 | Analytics visualizations | Admins can explore supported trends and distributions using actual data. |
| PR-012 | P1 | CSV export | Authorized administrators can export filtered report data. |
| PR-013 | P1 | Explanation and derived metrics | The UI can show supported model insights and price-per-area values where valid. |

Detailed requirement IDs, exact validations, API schemas, permissions, error formats, and test cases will be defined in the SRS.

## 8. Prediction Experience and User Expectations

### 8.1 Prediction inputs

The planned input fields, subject to a final data-quality review, are:

- Supported location.
- Area and its defined basis/unit.
- BHK/bedroom count.
- Bathroom count.
- Balcony count, if sufficiently reliable.
- Floor information.
- Furnishing status.
- Transaction type.
- Ownership category.
- Facing as an optional field if data quality supports it.

The live form must not display a field solely because it appears in the original document. The field must be represented reliably in the audited dataset and final model schema. Garage/parking is not a first-release input unless the data audit demonstrates that it can be used consistently; it has substantial missingness in the supplied CSV.

### 8.2 Result expectations

A successful result should include:

- Estimated price in INR, formatted for Indian readers (including lakh/crore presentation where appropriate).
- A summary of the property inputs used.
- The model version or a reference to published model information where useful.
- A clear statement that this is a model estimate based on historical listing data, not a guaranteed market or transaction price.
- A derived price-per-square-foot figure only when the normalized area definition supports that calculation.

The product must not show invented confidence intervals, unsupported accuracy percentages, or fabricated explanatory claims.

### 8.3 Unsupported inputs

The product must define a policy for unsupported locations, invalid units, missing required values, and values outside the supported schema. It must either reject the request with a clear message or apply a documented, model-validated fallback. It must not silently imply reliable coverage where none has been evaluated.

## 9. Dataset and ML Product Requirements

### 9.1 Dataset under evaluation

The user-supplied archive contains `house_prices.csv`. A preliminary audit of the supplied file reported:

| Observation | Preliminary result |
|---|---:|
| Raw rows | 187,531 |
| Columns | 21 |
| Distinct values in `location` | 81 |
| `Amount(in rupees)` values parsed by the current simple Lac/Cr parser | 177,847 |
| `Call for Price` records | 9,684 |
| Missing `Carpet Area` | 80,673 |
| Missing `Super Area` | 107,685 |
| Missing `Price (in rupees)` | 17,665 |
| Missing `Car Parking` | 103,357 |
| Missing `facing` | 70,233 |
| Missing `overlooking` | 81,436 |
| Missing `Society` | 109,678 |
| Fully blank `Dimensions` and `Plot Area` | Both columns |

**Critical preliminary finding:** The `Index` column is unique per row, but after excluding `Index`, **119,339 rows are duplicate occurrences across the remaining 20 columns**; this leaves 68,192 unique row combinations before other cleaning. This is a serious data-quality issue, not a final deduplication decision. Phase 1 must reproduce the count, establish why the rows repeat, define a documented duplicate policy, and prevent repeated identical rows from inflating evaluation through train/test leakage or unintended weighting.

These figures were calculated from the archive supplied in this conversation. They are preliminary audit results and must be reproduced by a committed or documented audit script before the dataset is accepted for training. The 81 `location` values are categorical location labels and must be normalized/semantically checked; they must not be presented as verified coverage of all Indian cities.

### 9.2 Data provenance and licence

- Verify the original dataset source, exact version, licence, attribution requirements, and redistribution rules before committing raw data to a public repository or packaging it for deployment.
- The uploaded archive itself did not include sufficient licence evidence to approve redistribution.
- Maintain a dataset card documenting source, retrieval date, version/fingerprint, licence status, intended use, limitations, and cleaning decisions.
- Keep raw listing data out of public source control unless licence terms explicitly permit redistribution.

### 9.3 Data preparation expectations

- Convert verified price formats such as `42 Lac` and `1.40 Cr` to numeric INR values through tested, explicit rules.
- Exclude `Call for Price` and invalid/unparseable target values from supervised training and report the counts/reasons.
- Treat Carpet Area and Super Area as distinct concepts; convert only verified units. Regional units whose exact conversion is ambiguous must not be guessed.
- Establish a consistent area feature strategy after reviewing overlap, unit mix, and missingness.
- Audit exact and near-duplicate records before the final split and report the effect of deduplication.
- Exclude `Index` as a model feature. Treat `Price (in rupees)` as a potential target-derived/per-area field and exclude it from predictors by default until its meaning and leakage risk are confirmed.
- Avoid raw `Description` as a first-release predictor because it may contain price or target-revealing information. Extract structured details from `Title` only where justified and testable.
- Handle missing values and categorical encoding within a fitted training pipeline, with transformations fitted only on training data.
- Investigate extreme prices and area values rather than deleting them blindly.

### 9.4 Model expectations

- Treat the task as supervised regression for a continuous listing-price target in INR.
- Compare a simple `DummyRegressor` baseline with appropriate regression candidates. Candidate models may include Linear/Ridge Regression, Decision Tree Regressor, Random Forest Regressor, and HistGradientBoosting Regressor.
- Use a reproducible train/validation/test process and an untouched holdout test set for final reporting.
- Report MAE, RMSE, and R², and report location/segment-level performance where sufficient data exists.
- Do not use standard Logistic Regression for direct continuous house-price prediction.
- Persist fitted preprocessing and the selected estimator together as one versioned pipeline artifact wherever feasible.
- Record model version, dataset fingerprint/version, training date, target units, feature schema, dependency versions, evaluation results, and known limitations in metadata.
- Review and explicitly promote a model version; the live service must never retrain it during a prediction request.

## 10. High-Level Architecture and Technology Direction

### 10.1 Architecture decision

Use a **monorepo with independently runnable and deployable applications**. Service boundaries are maintained through documented HTTP APIs, not direct imports of another service's application code.

```text
Browser
  |
  v
Next.js + TypeScript frontend
  |  HTTP/JSON
  v
Django REST Framework application backend ----------> Application database
  |                                                  (users, profiles, predictions)
  |  Protected service-to-service HTTP
  v
Independent Python inference service
  |
  v
Approved scikit-learn pipeline artifact

Offline ML training workflow
  -> audit / clean / feature engineering / train / evaluate
  -> reviewed, versioned artifact release
  -> inference service
```

### 10.2 Technology direction

| Layer | Planned choice | Notes |
|---|---|---|
| Frontend | Next.js (16.x LTS) + TypeScript | Responsive pages, forms, dashboards, charts, typed API client. |
| Application backend | Python + Django (5.2 LTS) REST Framework | Authentication, permissions, business rules, persistence, reporting. |
| Inference service | Independent Python HTTP service (FastAPI) | Approved for standalone HTTP prediction serving and Pydantic schema validation. |
| ML training | Python, pandas, NumPy, scikit-learn | Offline data audit, model training, evaluation, and artifact creation. |
| Artifact persistence | joblib + metadata.json | Full fitted pipeline plus metadata; never accept arbitrary user-uploaded artifacts. |
| Local database | SQLite | Standard zero-configuration local development database. |
| Production database | PostgreSQL | Enforced for production deployment (no silent fallback to SQLite). |
| API contracts | Versioned OpenAPI 3.0 YAML | Formal contracts for frontend ↔ backend and backend ↔ inference. |
| Testing | Python test suite (pytest), frontend tests (Node test runner), linting and builds | Test each service independently and then test integrated flows. |

### 10.3 Independent deployability requirements

- Each deployable application has its own dependencies, startup command, configuration, tests, and documented health/readiness behavior.
- Frontend calls the Django application backend, not the inference service directly.
- Django calls inference over a protected HTTP interface; inference does not access user-account or prediction-history tables.
- Offline training uses a separate environment and does not run as part of a live request.
- Shared contracts may be kept in the monorepo, but runtime service boundaries remain intact.
- The project should be runnable locally without Docker initially. Docker Compose can be introduced later if it improves developer experience.

## 11. User Experience and Accessibility

- Responsive and usable on mobile, tablet, and desktop.
- Clear navigation and consistent visual components for public, user, and admin areas.
- Accessible labels, keyboard navigation, visible focus states, and understandable validation messages.
- Loading, success, empty, and failure states for forms, prediction requests, history, charts, and reports.
- INR values use consistent Indian number formatting.
- Supported locations and feature options come from the approved dataset/schema, not fabricated hard-coded lists.
- Admin metrics and model scores come from real records and saved evaluation results.

## 12. Security, Privacy, and Reliability Expectations

- Use Django-supported password hashing and a documented authentication approach appropriate for the deployment domains.
- Enforce role and record-ownership checks on the server; frontend route hiding is not sufficient authorization.
- Keep service credentials, database credentials, tokens, and production secrets out of source control and the browser bundle.
- Configure CORS narrowly; use CSRF protection where cookie/session authentication requires it; use HTTPS in production.
- Validate incoming values and model outputs server-side. Do not return stack traces, secrets, internal filesystem paths, or unnecessary personal information to clients.
- Apply bounded timeouts and safe error handling to service-to-service calls; never replace an error with a fake price.
- Keep logs useful for debugging while excluding passwords, tokens, and unnecessary personal data.
- Load only trusted, reviewed model artifacts and verify artifact/metadata compatibility at startup.

Detailed security controls and test scenarios will be defined in the SRS and implementation/test plan.

## 13. Product Acceptance at Release Level

The first release can be considered functionally ready for final local review only when:

1. A user can register/sign in, submit a valid supported property, receive an estimate, and find the saved prediction in their own history.
2. Invalid or unsupported inputs produce clear errors and do not produce a fabricated estimate.
3. Users cannot view or change another user's private records; administrator functions are server-protected.
4. Administrators can view real user/prediction summaries and filter prediction records by date.
5. The model's dataset, cleaning policy, baseline comparison, MAE/RMSE/R², and limitations are documented.
6. The frontend, Django backend, and inference service can be started and tested independently.
7. Integrated end-to-end tests pass in a clean local setup, with remaining issues documented.
8. The README enables a developer to reproduce setup and required tests without undocumented local state.

Online deployment is a separate release gate and is not considered complete until production smoke tests confirm authentication, inference, persistence, and security configuration.

The exact test cases and pass/fail assertions will be specified in the SRS.

## 14. Phase-Wise Delivery Roadmap

The roadmap is intentionally high-level; the detailed task list, requirement mapping, and exit tests belong in `IMPLEMENTATION_PLAN.md` and the SRS.

| Phase | Focus | Expected deliverable | Exit gate |
|---|---|---|---|
| Phase 0 | Requirements and architecture | Approved PRD/SRS scope, architecture boundaries, unresolved decisions list | Product owner approves requirements; blockers are resolved or explicitly accepted. |
| Phase 1 | Dataset audit and preparation | Reproducible audit, data dictionary, source/licence assessment, price/area rules, duplicate policy | Audit findings reviewed; target and area definitions are approved. |
| Phase 2 | Offline ML training and evaluation | Baseline/model comparison, reports, candidate pipeline artifact and metadata | Metrics and limitations reviewed; artifact smoke test passes. |
| Phase 3 | Independent inference service | Versioned prediction interface, model loading, validation, readiness, tests | Service runs independently and returns validated predictions/errors. |
| Phase 4 | Django application backend | Authentication, roles, data persistence, prediction orchestration, admin/report APIs | Backend and authorization tests pass. |
| Phase 5 | Next.js frontend | Public pages, authentication UI, prediction flow, history, profile, admin interface | Main user journeys work against the real API. |
| Phase 6 | Integration and quality assurance | Integrated flows, security checks, bug fixes, documentation updates | All approved P0 acceptance criteria pass. |
| Phase 7 | Local release | Setup scripts, environment examples, README, test evidence, release checklist | Clean local setup is reproducible. |
| Phase 8 | Online deployment | Separate deployment configurations, production database, secrets/security, smoke tests | Production verification passes before the release is declared complete. |

**Phase gate rule:** Do not start the next phase merely because code has been written. Review the current deliverable, test evidence, open defects, and acceptance criteria first. The product owner explicitly approves progression between phases.

## 15. Key Risks and Mitigations

| Risk | Product impact | Mitigation |
|---|---|---|
| Large number of repeated rows | Evaluation leakage and distorted model behavior | Reproduce duplicate audit, define deduplication policy, and split data only after leakage review. |
| Unverified dataset licence | Restrictions on source control or redistribution | Verify original terms; keep raw data out of public release until permission is clear. |
| Listing prices differ from final sale prices | Users may over-trust an estimate | Label outputs accurately and display limitations. |
| Area units are inconsistent or region-dependent | Incorrect estimates | Convert only verified units; reject or omit ambiguous values. |
| City coverage is uneven | Performance differs by location | Audit location coverage and report segment-level error; constrain claims to supported inputs. |
| High missingness in features | Unstable or unusable inputs | Select first-release features based on data coverage and quality; test missing-value handling. |
| Training/inference mismatch | Incorrect production results | Save preprocessing and estimator together and test the published artifact. |
| Model artifact incompatibility | Inference startup/runtime failure | Pin compatible dependencies, validate metadata, and run readiness/smoke tests. |
| Service or database outage | Incomplete prediction workflow | Use timeouts, safe errors, health checks, and deployment verification. |
| Unauthorized data access | Privacy/security breach | Enforce ownership/role checks in the backend and test negative cases. |

## 16. Approved Architecture Decisions & Remaining Open Issues

### 16.1 Approved Phase 0 Decisions
1. **Inference framework:** **FastAPI** is approved for the independent `inference-service/`. Django REST Framework remains the application backend.
2. **Authentication design:** **Django REST Framework with SimpleJWT** is approved (short-lived in-memory access token, refresh token in HttpOnly cookie with rotation/revocation, authoritative backend authorization). Full feature implementation is scheduled for Phase 4.
3. **Database strategy:** **SQLite** is approved for local development; **PostgreSQL** is approved and required for production deployment (enforced in `config.settings.production` without silent SQLite fallback).

### 16.2 Remaining Open Decisions (Pending Evidence or Relevant Phases)
1. **Dataset licence and provenance:** verify the exact original source/version, applicable licence, attribution, and redistribution permissions before any dataset publication.
2. **Duplicate strategy:** establish why records repeat when `Index` is excluded and approve the deduplication policy before splitting data for model evaluation.
3. **Area strategy:** decide how Carpet Area and Super Area are handled, which units can be converted reliably, and how the area basis is represented.
4. **Location policy:** normalize aliases/casing and decide how to handle unsupported or low-sample locations.
5. **Hosting and domain:** finalize production hosting provider and public domain after local acceptance tests.
6. **Data retention and export:** finalize retention expectations and the fields permitted in administrator CSV exports before deployment.
7. **Model benchmark:** reassess the proposed 10% MAE-improvement target after a valid baseline is measured, without manipulating the evaluation to force a pass.

## 17. Relationship to Other Project Documents

This PRD describes **why the product exists, who it serves, what capabilities it should provide, and what outcomes define success**. It is not intended to duplicate lower-level implementation specifications.

| Document | Responsibility |
|---|---|
| `SRS.md` | Detailed functional/non-functional requirements, input rules, expected behavior, roles/permissions, API request/response contracts, error handling, and testable acceptance criteria. |
| `ARCHITECTURE.md` | Service boundaries, component interactions, data flows, runtime configuration, and deployment model. |
| `IMPLEMENTATION_PLAN.md` | Phase tasks, dependencies, deliverables, testing checklist, exit gates, and approval tracking. |
| `DATASET_ML_SPEC.md` | Dataset audit, data dictionary, license/provenance, cleaning rules, feature definitions, split strategy, model experiments, and evaluation. |
| `README.md` | Developer setup, commands, environment variables, troubleshooting, and links to the project documentation. |

Any change that affects product scope, role capabilities, supported inputs, user-visible behavior, or success criteria should be reflected in the PRD first, then traced into the SRS and the relevant implementation plan.

## 18. Glossary

| Term | Meaning |
|---|---|
| Listing price | Advertised asking price; not necessarily the final property transaction price. |
| Target leakage | Use of information during model training that would not legitimately be available at prediction time or that reveals the target. |
| Training | Offline process that prepares data, fits preprocessing, trains candidate models, and evaluates performance. |
| Inference | Applying an already-trained and approved pipeline to new valid inputs to generate an estimate. |
| Model artifact | Saved fitted preprocessing and estimator plus metadata required to identify and load them. |
| MAE | Mean Absolute Error, the average absolute difference between predicted and actual target values. |
| RMSE | Root Mean Squared Error, an error metric that penalizes larger errors more strongly. |
| R² | Coefficient of determination; should be interpreted alongside MAE/RMSE and the target distribution. |
| Monorepo | One source repository containing multiple applications that can still have separate dependencies and deployment lifecycles. |

## 19. References and Source Notes

- User-provided reference document: *Real Estate Price Prediction Using Python and ML* (7-page Word document). It is the source for the original user/admin capabilities and original Django-based concept.
- User-provided dataset archive: `archive.zip`, containing `house_prices.csv`. Preliminary audit figures in Section 9 were recomputed from this supplied file on 22 October 2026.
- Candidate original dataset page: [Kaggle — House Price by Juhi Bhojani](https://www.kaggle.com/datasets/juhibhojani/house-price). The original source licence and redistribution permissions remain pending verification; a public page or a third-party repository is not, by itself, proof that the uploaded archive may be redistributed.

---

## Approval Record

- **Document status:** Ready for product-owner review and sign-off.
- **Approved by:** Pending.
- **Approval date:** Pending.
- **Implementation authorization:** Not granted by this document alone. Begin development only after the owner approves the PRD/SRS and the applicable phase plan.
