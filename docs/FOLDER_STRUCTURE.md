# Canonical Repository Folder Structure

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Status | Canonical Repository Structure Reference |
| Last updated | 22 October 2026 |

---

## 1. Top-Level Monorepo Architecture

```text
RealEstatePrediction/
├── frontend/                              # Next.js 16 + TypeScript web application
│   ├── public/                            # Static public assets
│   ├── src/
│   │   ├── app/                           # App Router routes and page layouts
│   │   │   ├── (auth)/login/              # Authentication routes
│   │   │   ├── (public)/about/            # Public information routes
│   │   │   ├── admin/                     # Administrator dashboard routes
│   │   │   ├── dashboard/                 # User prediction history routes
│   │   │   ├── predict/                   # Property input & estimate routes
│   │   │   ├── layout.tsx                 # Root HTML/CSS layout
│   │   │   └── page.tsx                   # Scaffold home page
│   │   ├── components/                    # Reusable UI components
│   │   ├── features/                      # Domain feature modules
│   │   ├── hooks/                         # React hooks
│   │   ├── lib/                           # Utility libraries and API client
│   │   │   └── api-client.ts              # Typed API client helper
│   │   └── types/                         # Shared TypeScript types
│   ├── tests/                             # Unit and component tests
│   │   └── api_client.test.ts             # Native TypeScript unit test
│   ├── e2e/                               # End-to-end browser tests
│   ├── eslint.config.mjs                  # ESLint 9 Flat Config
│   ├── next.config.mjs                    # Next.js configuration
│   ├── package.json                       # Next.js 16.4.2 & React 19 dependencies
│   ├── package-lock.json                  # Pinned npm dependency lockfile
│   ├── tsconfig.json                      # TypeScript configuration
│   └── .env.example                       # Frontend environment template
│
├── backend/                               # Django 5.2 LTS + DRF Application Backend
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py                    # Base Django & DRF settings (SimpleJWT configured)
│   │   │   ├── development.py             # Local development settings (SQLite)
│   │   │   └── production.py              # Production settings (Strict PostgreSQL enforced)
│   │   ├── asgi.py                        # ASGI entrypoint
│   │   ├── urls.py                        # Root URL routing (/api/v1/health/)
│   │   └── wsgi.py                        # WSGI entrypoint
│   ├── apps/
│   │   ├── accounts/                      # User authentication and profile app
│   │   ├── properties/                    # Property metadata and locations app
│   │   ├── predictions/                   # Prediction orchestration app
│   │   │   └── clients/                   # Protected HTTP boundary for inference service
│   │   │       └── inference_client.py    # Inference HTTP client
│   │   └── analytics/                     # Admin summaries and reporting app
│   ├── tests/
│   │   ├── test_health.py                 # Health endpoint tests
│   │   └── test_production_settings.py    # PostgreSQL enforcement tests
│   ├── manage.py                          # Django management CLI
│   ├── pytest.ini                         # Pytest configuration
│   ├── requirements.txt                   # Pinned Django 5.2, DRF 3.18, SimpleJWT, psycopg
│   └── .env.example                       # Backend environment template
│
├── inference-service/                     # Standalone Python HTTP Service (FastAPI)
│   ├── app/
│   │   ├── api/                           # API route definitions
│   │   │   └── routes.py                  # /health/live, /health/ready, /api/v1/predict
│   │   ├── config/                        # Service settings
│   │   │   └── settings.py                # Environment-driven configuration
│   │   ├── model/                         # Model loading logic
│   │   │   └── loader.py                  # Startup artifact loader & truthful readiness
│   │   ├── schemas/                       # Pydantic request/response schemas
│   │   │   └── predict.py                 # PropertyPredictionRequest schema
│   │   ├── services/                      # Inference evaluation service
│   │   │   └── predict_service.py         # Prediction logic (fails safely if no model)
│   │   └── main.py                        # FastAPI application entrypoint
│   ├── artifacts/                         # Approved model pipeline storage (.joblib)
│   │   └── README.md                      # Artifact provenance instructions
│   ├── tests/                             # Inference test suite
│   │   └── test_health.py                 # Liveness and truthful readiness tests
│   ├── requirements.txt                   # Independent FastAPI runtime dependencies
│   ├── README.md                          # Inference service runbook
│   └── .env.example                       # Inference environment template
│
├── ml/
│   └── training/                          # Offline-only ML Training Pipeline
│       ├── configs/                       # Hyperparameter and feature configurations
│       │   └── model_config.yaml          # Target, leakage exclusions, model candidates
│       ├── data/                          # Segregated data directories (gitignored)
│       │   ├── raw/                       # Unmodified source listings
│       │   ├── interim/                   # Cleaned intermediate data
│       │   ├── processed/                 # Final feature-engineered arrays
│       │   └── external/                  # Supplementary reference data
│       ├── experiments/                   # Experiment tracking artifacts
│       ├── reports/                       # Evaluation reports (MAE, RMSE, R²)
│       ├── scripts/                       # CLI execution scripts
│       │   ├── validate_data.py           # Dataset audit and profiling entrypoint
│       │   ├── train.py                   # Baseline and candidate model training
│       │   ├── evaluate.py                # Holdout test set evaluation
│       │   └── promote_model.py           # Validated model promotion to inference-service
│       ├── src/real_estate_ml_training/   # Reusable ML package modules
│       │   ├── audit.py                   # Raw data audit functions
│       │   ├── clean.py                   # Price parser and unit normalizers
│       │   ├── features.py                # Column transformers and encoders
│       │   └── models.py                  # Candidate regression models
│       ├── tests/                         # Unit tests for preprocessing & ML pipeline
│       ├── pyproject.toml                 # Package definition
│       ├── requirements-training.txt      # scikit-learn, pandas, numpy dependencies
│       └── README.md                      # Training workflow documentation
│
├── contracts/                             # Formal OpenAPI 3.0 Specifications
│   ├── application-api.yaml               # Next.js ↔ Django public contract
│   └── inference-api.yaml                 # Django ↔ Inference service internal contract
│
├── docs/                                  # Canonical Documentation & Specifications
│   ├── ARCHITECTURE.md                    # System architecture & service boundaries
│   ├── DATASET_ML_SPEC.md                 # Dataset audit profile & ML specifications
│   ├── DEPLOYMENT_GUIDE.md                # Phase 8 production deployment guide
│   ├── FOLDER_STRUCTURE.md                # Canonical repository folder structure (this file)
│   ├── IMPLEMENTATION_PLAN.md             # Phase-gated implementation roadmap
│   ├── OPEN_DECISIONS.md                  # Approved decisions and risk register
│   ├── PHASE0_ALIGNMENT_REPORT.md         # Phase 0 consistency alignment report
│   ├── PRD.md                             # Product Requirements Document (Canonical v1.0)
│   ├── SCAFFOLDING_REPORT.md              # Initial scaffold verification evidence
│   ├── SRS.md                             # Software Requirements Specification (Canonical v1.0)
│   └── TESTING_PLAN.md                    # Quality assurance and testing strategy
│
├── prompts/                               # Guiding prompt artifacts
│   └── ANTIGRAVITY_SCAFFOLDING_PROMPT.md  # Original scaffold specification
│
├── scripts/                               # PowerShell Automation Scripts
│   ├── setup_dev.ps1                      # Local development setup script
│   ├── run_local.ps1                      # Multi-terminal service runner guide
│   └── check_scaffold.ps1                 # Automated structural integrity test
│
├── .gitignore                             # Hardened Git exclusions
├── .env.example                           # Root environment variable template
├── README.md                              # Repository overview and quickstart guide
└── compose.yaml                           # Multi-service container blueprint (optional)
```
