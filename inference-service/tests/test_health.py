from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness_endpoint():
    """Verify GET /health/live returns 200 alive status."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert data["service"] == "inference-service"

def test_readiness_endpoint_truthfully_returns_503_when_no_artifact():
    """Verify GET /health/ready returns 503 not_ready when no model artifact is loaded."""
    response = client.get("/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert "not loaded or missing" in data["reason"]

def test_prediction_returns_503_when_model_not_ready():
    """Verify POST /api/v1/predict returns 503 without fabricating prices when model is not ready."""
    payload = {
        "location": "Whitefield",
        "area_value": 1200.0,
        "area_basis": "CARPET",
        "bhk": 2,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 503
    assert "not ready" in response.json()["detail"].lower()
