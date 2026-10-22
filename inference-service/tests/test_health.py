import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.model import model_loader

client = TestClient(app)


def test_liveness_endpoint_returns_200_regardless_of_model():
    """Verify GET /health/live returns 200 alive independently of model status."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert data["service"] == "inference-service"


def test_readiness_endpoint_truthfully_returns_503_when_no_artifact(monkeypatch):
    """Verify GET /health/ready returns 503 not_ready when model_loader is unloaded."""
    monkeypatch.setattr(model_loader, "_model", None)
    monkeypatch.setattr(model_loader, "_metadata", None)

    response = client.get("/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert data["model_version"] is None
    # Ensure no file system paths or stack traces leaked
    assert "C:" not in str(data)
    assert "/" not in data.get("reason", "")
    assert "\\" not in data.get("reason", "")


def test_readiness_endpoint_returns_200_when_loaded(monkeypatch):
    """Verify GET /health/ready returns 200 ready when valid model and metadata are loaded."""
    dummy_model = lambda: None
    dummy_meta = {"model_id": "test_model_v1"}

    monkeypatch.setattr(model_loader, "_model", dummy_model)
    monkeypatch.setattr(model_loader, "_metadata", dummy_meta)

    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["model_version"] == "test_model_v1"
