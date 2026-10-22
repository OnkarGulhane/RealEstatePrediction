import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.model import model_loader

client = TestClient(app)


def test_real_artifact_smoke():
    """
    End-to-end smoke test using the actual Phase 2 model artifact and metadata if present locally.
    Evaluates one legitimate schema-valid property request and confirms a finite positive INR prediction.
    """
    art_path = settings.resolved_artifact_path
    meta_path = settings.resolved_metadata_path

    if not art_path.exists() or not meta_path.exists():
        pytest.skip(f"Local Phase 2 artifacts not found at {art_path}; skipping real-model smoke test.")

    # 1. Load the actual Phase 2 artifact via default configured path
    loaded = model_loader.load_artifact()
    assert loaded is True, f"Failed to load real artifact: {model_loader.last_error}"
    assert model_loader.is_ready() is True

    # 2. Verify health readiness
    res_ready = client.get("/health/ready")
    assert res_ready.status_code == 200
    ready_data = res_ready.json()
    assert ready_data["status"] == "ready"
    assert ready_data["model_version"] == "real_estate_hist_gradient_boosting_log_tuned_v1"

    # 3. Verify metadata endpoint returns sanitized summary
    res_meta = client.get("/api/v1/model/metadata")
    assert res_meta.status_code == 200
    meta_data = res_meta.json()
    assert meta_data["model_id"] == "real_estate_hist_gradient_boosting_log_tuned_v1"
    assert meta_data["target"]["unit"] == "INR"
    assert meta_data["features"]["total_features"] == 22
    assert meta_data["test_evaluation"]["holdout_mae_inr"] == 2693927.27

    # 4. Predict for a legitimate property: 2 BHK, 1200 sqft Carpet in Thane
    payload = {
        "schema_version": "1.0",
        "location": "Thane",
        "area_value": 1200.0,
        "area_basis": "CARPET",
        "bhk": 2,
        "bathrooms": 2.0,
        "balcony": 1,
        "parking_spaces": 1.0,
        "furnishing": "Semi-Furnished",
        "transaction_type": "Resale",
        "status": "Ready to Move",
        "facing": "East",
        "ownership": "Freehold",
    }
    res_pred = client.post("/api/v1/predict", json=payload)
    assert res_pred.status_code == 200
    pred_data = res_pred.json()
    assert pred_data["estimated_price_inr"] > 0
    assert pred_data["currency"] == "INR"
    assert pred_data["model_version"] == "real_estate_hist_gradient_boosting_log_tuned_v1"
    assert pred_data["schema_version"] == "1.0"
    assert "request_id" in pred_data
    # Predicted price is around 81 Lakh INR (~8,103,904)
    assert 5000000 < pred_data["estimated_price_inr"] < 15000000
