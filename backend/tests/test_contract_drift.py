from pathlib import Path
import yaml
import pytest
from django.urls import get_resolver
from apps.predictions.serializers import PropertyPredictionInputSerializer
from apps.accounts.serializers import RegisterSerializer


def get_django_url_patterns():
    resolver = get_resolver()
    url_patterns = []

    def extract_patterns(patterns, prefix=""):
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                extract_patterns(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                full_path = prefix + str(pattern.pattern)
                url_patterns.append(full_path)

    extract_patterns(resolver.url_patterns)
    return url_patterns


class TestApplicationContractDrift:
    @classmethod
    def setup_class(cls):
        contract_path = Path(__file__).resolve().parent.parent.parent / "contracts" / "application-api.yaml"
        assert contract_path.exists(), f"Contract not found at {contract_path}"
        with open(contract_path, "r", encoding="utf-8") as f:
            cls.spec = yaml.safe_load(f)

    def test_openapi_info_and_server(self):
        assert self.spec["openapi"].startswith("3.0")
        assert self.spec["info"]["title"] == "Real Estate Price Prediction Platform — Application API"
        assert self.spec["info"]["version"] == "1.0.0"

    def test_all_contract_paths_exist_in_django_router(self):
        contract_paths = set(self.spec.get("paths", {}).keys())
        django_patterns = get_django_url_patterns()

        # Map django URL regex patterns to OpenAPI path format
        # E.g. "api/v1/predictions/<uuid:pk>/" -> "/predictions/{id}/"
        # "api/v1/auth/register/" -> "/auth/register/"
        normalized_django = set()
        for p in django_patterns:
            if p.startswith("api/v1/"):
                subpath = "/" + p[len("api/v1/"):]
                # Normalize parameter syntax
                subpath = subpath.replace("<uuid:pk>", "{id}")
                normalized_django.add(subpath)

        for path in contract_paths:
            assert path in normalized_django, f"Contract path {path} not found in Django registered URL routes: {normalized_django}"

    def test_prediction_input_schema_matches_serializer(self):
        schema = self.spec["components"]["schemas"]["PropertyPredictionInput"]
        contract_required = set(schema.get("required", []))

        serializer = PropertyPredictionInputSerializer()
        serializer_required = {
            name for name, field in serializer.fields.items() if field.required
        }

        assert contract_required == serializer_required
        assert "schema_version" in serializer_required
        assert "location" in serializer_required
        assert "area_value" in serializer_required
        assert "area_basis" in serializer_required

    def test_register_input_schema_matches_serializer(self):
        schema = self.spec["components"]["schemas"]["RegisterRequest"]
        contract_required = set(schema.get("required", []))

        serializer = RegisterSerializer()
        serializer_required = {
            name for name, field in serializer.fields.items() if field.required
        }

        assert contract_required == serializer_required
        assert "email" in serializer_required
        assert "password" in serializer_required
