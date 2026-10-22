# Standalone Real Estate Price Prediction — Inference Service

Standalone internal HTTP microservice built with **FastAPI** to evaluate residential property listing prices in Indian Rupees (INR) using the frozen, offline-trained Phase 2 scikit-learn pipeline.

---

## 1. Architectural Boundaries

- **Decoupled Architecture:** Operates completely independently of Django REST Framework and Next.js. Has no database connections, no user/account models, and does not perform online model fitting or data training.
- **Client Access:** Internal microservice designed to be called by Django. Direct browser calls are prohibited by architecture.
- **Local Bind:** Defaults to `127.0.0.1:8001` (not public `0.0.0.0`).
- **Artifact Protection:** The model artifact (`model_pipeline.joblib`) and paired metadata (`metadata.json`) are **local-only** and strictly ignored by Git. They must never be committed to source control.

---

## 2. Prerequisites & Setup (Windows PowerShell)

Run all commands from the repository root:

```powershell
# 1. Navigate to the repository root
cd e:\RealEstatePrediction

# 2. Create the inference virtual environment if not already created
python -m venv inference-service\.venv

# 3. Activate the inference virtual environment
.\inference-service\.venv\Scripts\Activate.ps1

# 4. Install pinned requirements
python -m pip install --upgrade pip
python -m pip install -r inference-service\requirements.txt
```

### Module Resolution Note
The serialized Phase 2 pipeline relies on `real_estate_ml_training.features.PropertyFeatureExtractor`. `ModelLoader` dynamically and deterministically resolves `ml/training/src` relative to the inference service root (`SERVICE_ROOT.parent / "ml" / "training" / "src"`). No machine-specific absolute `.pth` files or hand-edited virtual environments are required.

---

## 3. Preparing Model Artifacts & Configuration

The approved Phase 2 candidate model and metadata exist locally at:
- `ml/training/experiments/phase2/model_pipeline.joblib`
- `ml/training/experiments/phase2/metadata.json`

*(Note: `ml/training/scripts/promote_model.py` is a verification script that validates candidate artifact integrity and sanity; it does not copy files).*

Choose one of two preparation methods:

### Method A (Default: Direct Relative Resolution)
The default `settings.py` resolves relative to the `inference-service/` service root:
- `MODEL_ARTIFACT_PATH=../ml/training/experiments/phase2/model_pipeline.joblib`
- `MODEL_METADATA_PATH=../ml/training/experiments/phase2/metadata.json`

Copy `.env.example` to `inference-service/.env` without modifying paths:
```powershell
Copy-Item inference-service\.env.example inference-service\.env
```

### Method B (Local Copy into `inference-service/artifacts/`)
If you prefer keeping local copies inside the service directory:
```powershell
New-Item -ItemType Directory -Force -Path inference-service\artifacts
Copy-Item ml\training\experiments\phase2\model_pipeline.joblib inference-service\artifacts\model_pipeline.joblib
Copy-Item ml\training\experiments\phase2\metadata.json inference-service\artifacts\metadata.json
```
Then configure in `inference-service/.env`:
```text
MODEL_ARTIFACT_PATH=artifacts/model_pipeline.joblib
MODEL_METADATA_PATH=artifacts/metadata.json
```
*(Both `.joblib` and `.json` in `inference-service/artifacts/` remain strictly ignored by `.gitignore`)*.

### Key Environment Variables:
| Variable | Default | Purpose |
|---|---|---|
| `ENVIRONMENT` | `development` | Runtime mode (`development` or `production`). In `production`, `SERVICE_TOKEN` is mandatory. |
| `HOST` | `127.0.0.1` | Local loopback bind address. |
| `PORT` | `8001` | Service listening port. |
| `MODEL_ARTIFACT_PATH` | `../ml/training/experiments/phase2/model_pipeline.joblib` | Path relative to `inference-service/` (or absolute). |
| `MODEL_METADATA_PATH` | `../ml/training/experiments/phase2/metadata.json` | Path relative to `inference-service/` (or absolute). |
| `SERVICE_TOKEN` | *(optional in dev)* | Secret string for `X-Service-Token` header authentication. |

---

## 4. Running the Service

Start Uvicorn on `127.0.0.1:8001` from the repository root:

```powershell
.\inference-service\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir inference-service --host 127.0.0.1 --port 8001
```

---

## 5. Endpoints & Example Requests

### A. Health Liveness Probe (Unauthenticated)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/health/live" -Method GET
```
**Response (200 OK):**
```json
{
  "status": "alive",
  "service": "inference-service"
}
```

### B. Model Readiness Probe (Unauthenticated)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/health/ready" -Method GET
```
**Response (200 OK when ready):**
```json
{
  "status": "ready",
  "model_version": "real_estate_hist_gradient_boosting_log_tuned_v1"
}
```
*(If model artifact is missing or invalid, returns `503 Service Unavailable` with `status: "not_ready"` without leaking system paths).*

### C. Predict Property Price (Authenticated via `X-Service-Token`)
```powershell
$headers = @{
    "Content-Type" = "application/json"
    "X-Service-Token" = "your-secret-internal-service-token-here"
}

$body = @{
    schema_version = "1.0"
    location = "Thane"
    area_value = 1200.0
    area_basis = "CARPET"
    bhk = 2
    bathrooms = 2
    balcony = 1
    parking_spaces = 1
    furnishing = "Semi-Furnished"
    transaction_type = "Resale"
    status = "Ready to Move"
    facing = "East"
    ownership = "Freehold"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/predict" -Method POST -Headers $headers -Body $body
```
**Response (200 OK):**
```json
{
  "request_id": "7f8b9e6a-3c2d-4e5f-a1b2-c3d4e5f6a7b8",
  "estimated_price_inr": 8103904.75,
  "currency": "INR",
  "model_version": "real_estate_hist_gradient_boosting_log_tuned_v1",
  "schema_version": "1.0",
  "property_summary": {
    "location": "Thane",
    "area_value": 1200.0,
    "area_basis": "CARPET",
    "bhk": 2,
    "bathrooms": 2,
    "balcony": 1,
    "parking_spaces": 1
  },
  "disclaimer": "This estimate is generated by an offline-trained regression model based on historical listing data. It does not constitute a certified valuation or guaranteed market price."
}
```

### D. Model Metadata Probe (Authenticated via `X-Service-Token`)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/model/metadata" -Method GET -Headers $headers
```

---

## 6. Running Tests

Run the test suite using pytest inside the inference virtual environment:

```powershell
.\inference-service\.venv\Scripts\python.exe -m pytest inference-service/tests -v
```

---

## 7. Troubleshooting

- **503 on `/health/ready`:** Confirm `MODEL_ARTIFACT_PATH` and `MODEL_METADATA_PATH` in `.env` point to valid Phase 2 local files. The service checks file existence, JSON validity, target currency (`INR`), and 22-feature schema order.
- **`ModuleNotFoundError: No module named 'real_estate_ml_training'` on load:** Ensure `ml/training/src` exists in the repository. `ModelLoader` automatically adds it to `sys.path`.
- **`scikit-learn` version mismatch:** Verify that the installed `scikit-learn` matches the artifact's metadata version (`1.9.1`).
- **422 `UNSUPPORTED_LOCATION`:** The model was trained with 81 audited Indian city/locality names. Check `/api/v1/model/metadata` for supported location categories. Unknown locations return a defined error and are never silently estimated.
