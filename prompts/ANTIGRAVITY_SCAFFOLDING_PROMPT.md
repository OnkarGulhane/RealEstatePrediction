# Antigravity Prompt — Create the Project Scaffold Only

**Project:** Real Estate Price Prediction Platform — India  
**Prompt version:** 1.0  
**Scope:** Repository scaffolding and minimal smoke checks only. Do not implement product features or start the next development phase.

---

## ROLE

Act as a senior software architect and experienced full-stack/ML platform engineer. Create a clean, maintainable, Windows-friendly monorepo scaffold for this project. Prioritize clear service boundaries, reproducible setup, safe defaults, and verifiable results over unnecessary complexity.

## SOURCE-OF-TRUTH DOCUMENTS

Before editing anything, inspect the currently opened workspace and locate these documents if they are available:

1. `PRD.md`
2. `SRS.md`
3. `IMPLEMENTATION_PLAN.md`
4. `Real_Estate_Price_Prediction_FOLDER_STRUCTURE.md` or the latest approved folder-structure document

Also inspect any existing `docs/ARCHITECTURE.md`, `docs/DATASET_ML_SPEC.md`, `docs/TESTING_PLAN.md`, and `docs/DEPLOYMENT_GUIDE.md`.

Document authority:

- `PRD.md` defines product intent and scope.
- `SRS.md` defines detailed, testable software requirements.
- `IMPLEMENTATION_PLAN.md` controls phase order and approval gates.
- The approved folder structure defines the canonical repository layout.

If any document is absent, report it clearly and continue only with non-conflicting scaffold work. Do not invent missing requirements. If documents conflict, do not silently rewrite product decisions; record the conflict in `docs/OPEN_DECISIONS.md` and report it.

If approved documents exist at the repository root and the `docs/` copies do not exist, copy them into `docs/` without deleting or altering the originals. Do not overwrite a different existing file; compare first and report conflicts.

## PROJECT DECISIONS AND BOUNDARIES

Target architecture:

- `frontend/`: Next.js + TypeScript, App Router.
- `backend/`: Python + Django REST Framework; owns authentication, authorization, application data, prediction history, admin/reporting, and public application APIs.
- `inference-service/`: independently runnable Python HTTP service; loads an approved ML artifact and performs inference only.
- `ml/training/`: offline dataset audit, preprocessing, experiments, training, evaluation, and model-artifact creation.
- `contracts/`: versioned API contracts for Next.js ↔ Django and Django ↔ inference service.
- `docs/`: approved project documents and architecture/testing/deployment records.

Mandatory boundaries:

1. Browser/frontend calls Django only. It must never call the internal inference service directly.
2. Django calls the inference service through a documented, protected HTTP API. Do not import the inference service's application code into Django.
3. The inference service does not own or directly access Django user accounts, profiles, or prediction-history tables.
4. Offline training must not run during a live prediction request or during normal service startup.
5. Keep frontend, backend, inference, and training dependencies/configuration/tests independent.
6. Preserve preprocessing consistency: the eventual fitted preprocessing and estimator should be packaged as one versioned pipeline artifact where feasible.
7. Do not fabricate model artifacts, model scores, real market predictions, dataset facts, or successful test results.
8. The supplied Indian property dataset is not automatically approved for redistribution. Do not copy raw data into the scaffold or commit it to Git. Dataset licence, duplicate policy, price parsing, area conversion, and feature schema belong to a later dataset-audit phase.
9. Work locally first. Do not deploy, publish, push, or expose any service publicly.

### Inference framework decision

The planning documents currently identify **FastAPI as the recommended option, pending explicit approval**. For scaffold purposes only, create the minimum `inference-service/` skeleton using FastAPI and record this choice as **PROVISIONAL / REQUIRES OWNER APPROVAL** in an architecture decision note. Do not treat this as final approval for inference business logic or Phase 3. Do not begin full inference implementation in this task.

Authentication strategy, final package versions, hosting, production database, and dataset-cleaning policy may also remain pending. Represent them as documented decisions/placeholders; do not guess secrets or business rules.

---

## GOAL

Create a runnable *scaffold*, not the complete application. The result must have a coherent folder structure, minimal service entry points, configuration examples, dependency manifests, basic health routes, starter tests, documentation placeholders, and Windows-friendly commands. It must be clear which parts are scaffold placeholders and which checks actually passed.

## REQUIRED REPOSITORY STRUCTURE

Create or align the repository to this structure. Keep existing valuable files; do not blindly recreate a repository or nest a second project directory inside the workspace.

```text
real-estate-price-prediction/
├── frontend/                              # Next.js + TypeScript
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (public)/
│   │   │   ├── (auth)/
│   │   │   ├── predict/
│   │   │   ├── dashboard/
│   │   │   └── admin/
│   │   ├── components/
│   │   ├── features/
│   │   ├── lib/
│   │   ├── hooks/
│   │   └── types/
│   ├── tests/
│   ├── e2e/
│   ├── .env.example
│   ├── package.json
│   └── lockfile for the chosen package manager
│
├── backend/                               # Django REST Framework
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/
│   │   ├── properties/
│   │   ├── predictions/
│   │   │   └── clients/                   # HTTP client boundary for inference
│   │   └── analytics/
│   ├── tests/
│   ├── manage.py
│   ├── requirements.txt
│   ├── lock/ or documented pinned-dependency file, if selected
│   └── .env.example
│
├── inference-service/                     # Separate Python HTTP service
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── model/
│   │   ├── services/
│   │   └── config/
│   ├── artifacts/
│   │   ├── README.md
│   │   └── .gitkeep
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── ml/
│   └── training/                          # Offline-only
│       ├── data/
│       │   ├── raw/.gitkeep
│       │   ├── interim/.gitkeep
│       │   ├── processed/.gitkeep
│       │   └── external/.gitkeep
│       ├── src/real_estate_ml_training/
│       ├── scripts/
│       │   ├── validate_data.py
│       │   ├── train.py
│       │   ├── evaluate.py
│       │   └── promote_model.py
│       ├── configs/model_config.yaml
│       ├── experiments/
│       ├── reports/
│       ├── tests/
│       ├── requirements-training.txt
│       ├── pyproject.toml
│       └── README.md
│
├── contracts/
│   ├── application-api.yaml               # Next.js ↔ Django
│   └── inference-api.yaml                 # Django ↔ inference service
├── docs/
│   ├── PRD.md
│   ├── SRS.md
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── DATASET_ML_SPEC.md
│   ├── TESTING_PLAN.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── OPEN_DECISIONS.md
│   └── SCAFFOLDING_REPORT.md
├── scripts/
│   ├── setup_dev.ps1
│   ├── run_local.ps1
│   └── check_scaffold.ps1
├── .gitignore
├── .env.example
├── README.md
└── compose.yaml                            # Optional; do not require Docker initially
```

You may add essential files required for a framework to run (such as Django `apps.py`, `__init__.py`, Next.js config, ESLint config, or test config). Do not add unrelated folders or speculative features. If a path syntax such as `raw/.gitkeep` cannot be represented literally, create the directory and `.gitkeep` file inside it.

---

## IMPLEMENTATION INSTRUCTIONS

### Step 1 — Inspect and plan before changes

- Inspect workspace root, existing code, package manager lockfiles, Python installation, and Git status if available.
- Identify any existing work that must be preserved.
- Read the source-of-truth documents before choosing names and boundaries.
- Before editing, output a concise plan of intended changes and list missing documents/conflicts. Then continue with non-destructive scaffold work.
- Never delete or overwrite user files without a verified need and explicit approval.

### Step 2 — Create a minimal Next.js scaffold

- Use Next.js App Router with TypeScript and maintainable lint/type-check configuration.
- Respect an existing package manager/lockfile. If this is a new frontend with no package manager chosen, use npm and commit/update `package-lock.json`.
- Create a minimal home page that identifies the project and clearly labels itself as a scaffold; do not build the finished product UI.
- Add placeholder route directories or minimal route pages only where required to prove App Router structure. Do not implement registration, login, prediction workflows, dashboards, or visual polish in this task.
- Add a typed, configurable API base-URL helper that reads the correct public environment variable. Do not embed secrets in client-side variables.
- Include scripts for `dev`, `build`, `start`, `lint`, and `typecheck` (and `test` if a test runner is set up). Ensure scripts match the chosen Next.js version; do not use removed or invalid commands.
- Add `.env.example` with non-secret placeholders only, e.g. `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1`.

### Step 3 — Create a minimal Django REST backend scaffold

- Configure a modular Django project using separate settings modules for base/development/production. If splitting settings would complicate the first boot, keep one valid settings module and document the planned split; do not leave a broken import.
- Create the four Django apps: `accounts`, `properties`, `predictions`, and `analytics`; register valid apps in settings.
- Add a minimal API health endpoint such as `GET /api/v1/health/` returning a small JSON response with a clear service identifier. It must not claim that the ML model is available.
- Add starter tests for the health endpoint and basic project configuration.
- Ensure `python manage.py check`, `python manage.py migrate`, the test command, and `python manage.py runserver 8000` work in the documented environment.
- Do not implement full authentication, database domain models, prediction history, reporting, or inference integration now. Add TODOs linked to the relevant SRS requirement IDs only where helpful.

### Step 4 — Create a minimal inference-service scaffold

- Use FastAPI for the scaffold only as described in the provisional decision above. Add a minimal app entry point, configuration module, request/response schema placeholder, and separate tests.
- Add `GET /health/live` returning liveness, independent of model availability.
- Add `GET /health/ready` that reflects actual artifact readiness. If no reviewed model artifact exists, return a truthful not-ready status (for example HTTP 503); never fake model readiness.
- Add a prediction route only as a clearly incomplete placeholder if needed by the agreed API contract. If model artifacts are absent, it must return a documented unavailable response (HTTP 503), not a made-up price. Do not implement model loading/prediction logic beyond a safe placeholder in this scaffold phase.
- Include only runtime dependencies in `inference-service/requirements.txt`, pinned compatibly with the selected environment. Do not install the training stack into inference unnecessarily.
- Document that FastAPI remains provisional until the owner approves the architecture decision before full Phase 3 implementation.

### Step 5 — Create the offline ML training scaffold

- Create the package layout and placeholder modules for data audit, cleaning, feature engineering, training, evaluation, and artifact promotion.
- Include a valid `model_config.yaml` example with documented placeholder values, not hidden assumptions about final feature columns or model hyperparameters.
- Include `train.py`, `evaluate.py`, and `validate_data.py` entry points that fail with a clear “not implemented until Phase 1/2 approval” message or provide only harmless `--help` output. Do not pretend to train a model.
- `promote_model.py` must not create an artifact from placeholder data. It can be a documented stub until artifact validation/promotion is specified.
- Do not train on or copy the uploaded dataset during scaffolding. Do not create `model.pkl`, `encoder.pkl`, `model_pipeline.joblib`, fabricated metadata, accuracy scores, or synthetic market data.
- Put instructions in `ml/training/README.md` saying the dataset audit and licence must be approved before using/redistributing raw data.

### Step 6 — API contracts and configuration placeholders

- Create valid, syntactically correct OpenAPI YAML files for the minimal scaffold routes that actually exist (health/readiness). Mark product endpoints as planned/not implemented rather than falsely representing them as working.
- Use versioned paths where appropriate; keep the planned application and inference APIs separate.
- Add environment examples for each service. Use placeholders only; never create real credentials.
- Explain local default ports: Next.js `3000`, Django `8000`, inference service `8001`.
- Do not force CORS/auth behavior that assumes final auth design; add clearly documented environment placeholders and leave production hardening for the relevant approved phase.

### Step 7 — Documentation and operational scripts

- Create/update `README.md` with architecture, folder responsibilities, prerequisites, setup commands for Windows PowerShell, per-service start commands, test commands, and explicit notes about what is not implemented yet.
- Create `docs/ARCHITECTURE.md` with the actual scaffold state, service boundaries, local ports, and the provisional FastAPI decision.
- Create `docs/OPEN_DECISIONS.md` listing unresolved decisions without pretending they are approved.
- Create `docs/SCAFFOLDING_REPORT.md` as the final implementation evidence report.
- Create `docs/DATASET_ML_SPEC.md`, `docs/TESTING_PLAN.md`, and `docs/DEPLOYMENT_GUIDE.md` as clearly marked starter documents if they do not already exist; do not overwrite approved detailed documents.
- Create Windows PowerShell scripts that use repo-relative paths, fail fast on errors, check prerequisites, and never silently delete files. `setup_dev.ps1` may install per-service dependencies only with an explicit usage note; `run_local.ps1` should start each service in separate terminals/processes or print reliable manual commands rather than hiding logs; `check_scaffold.ps1` should perform safe structural checks.
- `compose.yaml` is optional. Do not make Docker a prerequisite for local startup. If it is added, validate it and keep secrets out of the file.

### Step 8 — `.gitignore` and data safety

Add appropriate ignore rules for at least:

- `.env` and all real environment-specific secret files (while retaining `.env.example`)
- `node_modules/`, `.next/`, build output, test caches
- Python virtual environments, `__pycache__/`, bytecode, test/lint caches
- local SQLite DBs and logs
- raw/interim/processed dataset files unless explicitly approved for version control
- generated model artifacts and experiment output unless a reviewed release policy permits them
- IDE and OS temporary files

Do not initialise Git or make commits unless a repository already exists or the user explicitly requests it. If Git is already initialized, inspect `git status` and preserve all existing changes.

---

## NON-GOALS — DO NOT IMPLEMENT NOW

This task is scaffold-only. Do not:

- implement complete authentication or RBAC;
- implement the actual property-price prediction model or train it;
- clean/transform the uploaded CSV or make final assumptions about units;
- create user, prediction, or report database business models beyond framework bootstrap;
- implement functional dashboards, charts, CSV exports, profile management, or history features;
- implement full inference/model-loading logic;
- create real admin accounts or hard-code credentials;
- make up dataset statistics, feature importance, model metrics, predictions, or test results;
- deploy, publish, push to GitHub, or expose services publicly;
- begin Phase 1 or any later implementation phase automatically;
- remove, rename, or replace project documents without inspecting them and preserving originals.

---

## VERIFICATION REQUIREMENTS

After scaffolding, actually run the checks supported by the environment. Do not merely state that they should pass.

Minimum checks:

1. **Frontend:** dependency installation if permitted, lint, TypeScript check, and production build.
2. **Backend:** install dependencies in its own virtual environment if permitted; run `python manage.py check`, migrations, health endpoint test, and Django test suite.
3. **Inference:** install dependencies in its own virtual environment if permitted; run lint/type check if configured, pytest for liveness/readiness, and verify readiness is not falsely successful without an artifact.
4. **Training scaffold:** verify Python modules compile/import and `--help` works where implemented; confirm there is no false model artifact or claimed metric.
5. **Contracts/docs:** parse OpenAPI YAML if a validator is available; validate paths match routes implemented in the scaffold.
6. **Structure/scripts:** run `check_scaffold.ps1` if available; otherwise execute equivalent checks and state why the script could not run.

If the environment lacks network/package installation permission, report those checks as `NOT RUN` and include the exact blocker. If any check fails, fix the scaffold issue and rerun the affected check. Never hide failures or label a check PASS without an executed result.

## FINAL RESPONSE REQUIRED FROM YOU

When finished, stop after scaffold verification and report:

1. What files/directories were created or updated.
2. The final folder tree (omit noisy generated folders like `node_modules` and virtual environments).
3. Exact local start commands for each service.
4. Exact test/build/check commands executed and their real results, labelled `PASS`, `FAIL`, or `NOT RUN`.
5. Pending decisions (especially provisional FastAPI approval, dataset licence, cleaning rules, authentication design, and production hosting).
6. Any unresolved errors or environmental blockers.
7. Phase status must be **SCAFFOLD READY FOR REVIEW**, not “project complete” and not “Phase 1 approved”.
8. STOP and ask for the project owner's approval before implementing features or starting Phase 1.

**Success means a clean, understandable, minimally runnable scaffold with truthful checks—not a pretend-complete application.**
