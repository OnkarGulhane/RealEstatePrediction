"""
Inference Service Client Boundary.
Responsible for making HTTP requests to the independent Python inference service.
Direct import of inference service code is strictly prohibited.
"""
import requests
from django.conf import settings

class InferenceClient:
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = (base_url or getattr(settings, 'INFERENCE_SERVICE_URL', 'http://localhost:8001')).rstrip('/')
        self.timeout = timeout or getattr(settings, 'INFERENCE_TIMEOUT_SECONDS', 10)

    def check_readiness(self) -> dict:
        """Query readiness endpoint of the inference service."""
        url = f"{self.base_url}/health/ready"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def predict(self, property_features: dict) -> dict:
        """
        Request prediction for validated property features.
        [PLANNED - Phase 4]: Orchestration between Django and Inference Service.
        """
        url = f"{self.base_url}/api/v1/predict"
        response = requests.post(url, json=property_features, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
