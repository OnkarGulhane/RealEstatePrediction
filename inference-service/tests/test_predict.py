import math
import numpy as np
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.model import model_loader

client = TestClient(app)


class MockPipeline:
    def __init__(self, return_val=7500000.0):
        self.return_val = return_val
        self.call_count = 0
        self.last_df = None

    def predict(self, X):
        self.call_count += 1
        self.last_df = X
        return np.array([self.return_val])


@pytest.fixture
def mock_model_env(monkeypatch):
    mock_pipe = MockPipeline(return_val=7500000.0)
    mock_meta = {
        "model_id": "test_hist_gb_v1",
        "target": {"unit": "INR"},
    }
    dummy_categories = {
        "location": {"thane", "whitefield"},
        "Furnishing": {"furnished", "semi furnished", "unspecified"},
        "Transaction": {"resale", "unspecified"},
        "Status": {"ready to move", "unspecified"},
        "facing": {"east", "unspecified"},
        "Ownership": {"freehold", "unspecified"},
    }
    dummy_raw_map = {
        "location": {"thane": "thane", "whitefield": "whitefield"},
        "Furnishing": {"furnished": "Furnished", "semi furnished": "Semi-Furnished", "unspecified": "Unspecified"},
        "Transaction": {"resale": "Resale", "unspecified": "Unspecified"},
        "Status": {"ready to move": "Ready to Move", "unspecified": "Unspecified"},
        "facing": {"east": "East", "unspecified": "Unspecified"},
        "Ownership": {"freehold": "Freehold", "unspecified": "Unspecified"},
    }

    monkeypatch.setattr(model_loader, "_model", mock_pipe)
    monkeypatch.setattr(model_loader, "_metadata", mock_meta)
    monkeypatch.setattr(model_loader, "_allowed_categories", dummy_categories)
    monkeypatch.setattr(model_loader, "_allowed_categories_raw", dummy_raw_map)
    return mock_pipe


def test_predict_returns_503_when_model_not_ready(monkeypatch):
    """When model is unloaded, predict endpoint returns 503 without fabricating prices."""
    monkeypatch.setattr(model_loader, "_model", None)
    monkeypatch.setattr(model_loader, "_metadata", None)

    payload = {
        "schema_version": "1.0",
        "location": "Thane",
        "area_value": 1200.0,
        "area_basis": "CARPET",
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "MODEL_NOT_READY"
    assert "request_id" in data["error"]


def test_predict_successful_call_single_predict_invocation(mock_model_env):
    """Valid request returns 200, strictly positive INR estimate, and invokes predict() once."""
    payload = {
        "schema_version": "1.0",
        "location": "Thane",
        "area_value": 1200.0,
        "area_basis": "CARPET",
        "bhk": 2,
        "bathrooms": 2.0,
        "balcony": 1,
        "parking_spaces": 1,
        "furnishing": "Semi-Furnished",
        "transaction_type": "Resale",
        "status": "Ready to Move",
        "facing": "East",
        "ownership": "Freehold",
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["estimated_price_inr"] == 7500000.0
    assert data["currency"] == "INR"
    assert data["model_version"] == "test_hist_gb_v1"
    assert data["schema_version"] == "1.0"
    assert "request_id" in data
    assert mock_model_env.call_count == 1
    assert len(mock_model_env.last_df) == 1


def test_predict_rejects_incompatible_schema_version(mock_model_env):
    """Rejects schema_version other than '1.0' with 422 and INCOMPATIBLE_SCHEMA_VERSION code."""
    payload = {
        "schema_version": "2.0",
        "location": "Thane",
        "area_value": 1200.0,
        "area_basis": "CARPET",
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "INCOMPATIBLE_SCHEMA_VERSION"
    assert "request_id" in data["error"]


def test_predict_rejects_missing_required_schema_version(mock_model_env):
    """Rejects requests omitting required schema_version with HTTP 422."""
    payload = {
        "location": "Thane",
        "area_value": 1200.0,
        "area_basis": "CARPET",
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "schema_version" in str(data["error"]["fields"])


def test_predict_rejects_missing_required_area_basis(mock_model_env):
    """Rejects requests omitting required area_basis with HTTP 422."""
    payload = {
        "schema_version": "1.0",
        "location": "Thane",
        "area_value": 1200.0,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "area_basis" in str(data["error"]["fields"])


def test_predict_rejects_fractional_parking_spaces(mock_model_env):
    """Rejects fractional parking counts like 1.5 with HTTP 422 instead of silent truncation."""
    payload = {
        "schema_version": "1.0",
        "location": "Thane",
        "area_value": 1200.0,
        "area_basis": "CARPET",
        "parking_spaces": 1.5,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "parking_spaces" in str(data["error"]["fields"])


def test_predict_rejects_invalid_area_values(mock_model_env):
    """Rejects negative, zero, or non-finite area values."""
    for bad_area in [-500.0, 0.0]:
        payload = {
            "schema_version": "1.0",
            "location": "Thane",
            "area_value": bad_area,
            "area_basis": "CARPET",
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422


def test_predict_rejects_invalid_floor_relationship(mock_model_env):
    """Rejects requests where floor_number > total_floors."""
    payload = {
        "schema_version": "1.0",
        "location": "Thane",
        "area_value": 1200.0,
        "area_basis": "CARPET",
        "floor_number": 10.0,
        "total_floors": 5.0,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "cannot exceed total_floors" in str(data)


def test_predict_rejects_unsupported_location(mock_model_env):
    """Rejects unsupported location with 422 UNSUPPORTED_LOCATION."""
    payload = {
        "schema_version": "1.0",
        "location": "Gotham City",
        "area_value": 1200.0,
        "area_basis": "CARPET",
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_LOCATION"
    assert "Gotham City" in data["error"]["message"]


def test_predict_rejects_invalid_category(mock_model_env):
    """Rejects unapproved categorical value with 422 INVALID_CATEGORY."""
    payload = {
        "schema_version": "1.0",
        "location": "Thane",
        "area_value": 1200.0,
        "area_basis": "CARPET",
        "furnishing": "Fully Royal Diamond Furnished",
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "INVALID_CATEGORY"


def test_predict_fails_safely_on_non_positive_or_non_finite_output(monkeypatch, mock_model_env):
    """Never returns zero, negative, NaN, or infinite price; returns safe 500 error."""
    for bad_val in [0.0, -150000.0, float("nan"), float("inf")]:
        bad_pipe = MockPipeline(return_val=bad_val)
        monkeypatch.setattr(model_loader, "_model", bad_pipe)

        payload = {
            "schema_version": "1.0",
            "location": "Thane",
            "area_value": 1200.0,
            "area_basis": "CARPET",
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INVALID_MODEL_OUTPUT"
        assert "non-positive or non-finite" in data["error"]["message"].lower()
