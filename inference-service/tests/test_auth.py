import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings, Settings
from app.model import model_loader

client = TestClient(app)


def test_auth_allows_request_when_token_matches(monkeypatch):
    """When SERVICE_TOKEN is configured, matching X-Service-Token is accepted."""
    monkeypatch.setattr(settings, "SERVICE_TOKEN", "test-secret-token-xyz")
    monkeypatch.setattr(model_loader, "_model", lambda: None)
    monkeypatch.setattr(model_loader, "_metadata", {"model_id": "test_m"})

    headers = {"X-Service-Token": "test-secret-token-xyz"}
    response = client.get("/api/v1/model/metadata", headers=headers)
    assert response.status_code == 200


def test_auth_denies_request_when_token_is_missing(monkeypatch):
    """When SERVICE_TOKEN is configured, missing header returns 401 Unauthorized."""
    monkeypatch.setattr(settings, "SERVICE_TOKEN", "test-secret-token-xyz")

    response = client.get("/api/v1/model/metadata")
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHORIZED"
    assert "missing" in data["error"]["message"].lower()


def test_auth_denies_request_when_token_is_invalid(monkeypatch):
    """When SERVICE_TOKEN is configured, incorrect header returns 403 Forbidden."""
    monkeypatch.setattr(settings, "SERVICE_TOKEN", "test-secret-token-xyz")

    headers = {"X-Service-Token": "wrong-token-abc"}
    response = client.get("/api/v1/model/metadata", headers=headers)
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "FORBIDDEN"
    assert "invalid" in data["error"]["message"].lower()


def test_health_routes_remain_unauthenticated_even_when_token_configured(monkeypatch):
    """Health endpoints (/health/live, /health/ready) remain open without service token."""
    monkeypatch.setattr(settings, "SERVICE_TOKEN", "test-secret-token-xyz")

    res_live = client.get("/health/live")
    assert res_live.status_code == 200

    res_ready = client.get("/health/ready")
    assert res_ready.status_code in [200, 503]  # Based on model load status, not auth


def test_production_settings_fails_startup_without_service_token():
    """Settings initialization in production mode requires a non-empty SERVICE_TOKEN."""
    with pytest.raises(ValueError, match="SERVICE_TOKEN must be configured"):
        Settings(
            ENVIRONMENT="production",
            SERVICE_TOKEN="",
        )
