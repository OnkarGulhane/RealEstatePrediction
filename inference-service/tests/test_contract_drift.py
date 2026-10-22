import yaml
from pathlib import Path
import pytest
from app.main import app
from app.schemas.predict import PropertyPredictionRequest
from app.config import SERVICE_ROOT

CONTRACT_PATH = SERVICE_ROOT.parent / "contracts" / "inference-api.yaml"


def test_contract_yaml_exists_and_parses():
    """Verify that contracts/inference-api.yaml exists and parses cleanly."""
    assert CONTRACT_PATH.exists(), f"Contract file not found at {CONTRACT_PATH}"
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    assert isinstance(spec, dict)
    assert spec.get("openapi") == "3.0.3"


def test_contract_drift_paths_and_operations():
    """Verify all implemented FastAPI paths and HTTP methods exist in the contract."""
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    paths = spec.get("paths", {})
    expected_paths = {
        "/health/live": ["get"],
        "/health/ready": ["get"],
        "/api/v1/predict": ["post"],
        "/api/v1/model/metadata": ["get"],
    }

    for path, methods in expected_paths.items():
        assert path in paths, f"Path '{path}' missing from OpenAPI contract"
        for method in methods:
            assert method in paths[path], f"Method '{method.upper()}' for '{path}' missing from contract"


def test_contract_drift_request_schema():
    """Verify PropertyPredictionRequest fields and required set exactly match contract schema properties."""
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    schemas = spec.get("components", {}).get("schemas", {})
    assert "PropertyPredictionRequest" in schemas
    req_schema = schemas["PropertyPredictionRequest"]

    # 1. Compare all property names
    contract_props = set(req_schema.get("properties", {}).keys())
    model_props = set(PropertyPredictionRequest.model_fields.keys())
    assert contract_props == model_props, (
        f"Contract schema differs from Pydantic model. "
        f"In contract only: {contract_props - model_props}. "
        f"In model only: {model_props - contract_props}."
    )

    # 2. Compare required fields set
    contract_required = set(req_schema.get("required", []))
    model_required = {
        name for name, field in PropertyPredictionRequest.model_fields.items() if field.is_required()
    }
    assert contract_required == model_required, (
        f"Required fields mismatch between OpenAPI contract and Pydantic model. "
        f"In contract required only: {contract_required - model_required}. "
        f"In model required only: {model_required - contract_required}."
    )

    # 3. Verify parking_spaces is typed as integer in both contract and schema
    assert req_schema["properties"]["parking_spaces"]["type"] == "integer"


def test_contract_drift_security_scheme():
    """Verify ServiceTokenAuth is defined and applied to protected routes in the contract."""
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    sec_schemes = spec.get("components", {}).get("securitySchemes", {})
    assert "ServiceTokenAuth" in sec_schemes
    assert sec_schemes["ServiceTokenAuth"]["type"] == "apiKey"
    assert sec_schemes["ServiceTokenAuth"]["in"] == "header"
    assert sec_schemes["ServiceTokenAuth"]["name"] == "X-Service-Token"

    # Protected routes must declare ServiceTokenAuth
    predict_sec = spec["paths"]["/api/v1/predict"]["post"].get("security", [])
    assert any("ServiceTokenAuth" in s for s in predict_sec)

    meta_sec = spec["paths"]["/api/v1/model/metadata"]["get"].get("security", [])
    assert any("ServiceTokenAuth" in s for s in meta_sec)
