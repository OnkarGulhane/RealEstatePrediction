"""
Inference Service Client Boundary.
Responsible for making HTTP requests to the independent Python FastAPI inference service.
Direct import of inference service code is strictly prohibited.
"""
import uuid
import logging
from typing import Dict, Any, Optional
import requests
from django.conf import settings

logger = logging.getLogger("backend.inference_client")


class InferenceClientError(Exception):
    def __init__(self, message: str, status_code: int = 500, code: str = "INFERENCE_ERROR", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.detail = detail or {}


class InferenceClient:
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None, service_token: Optional[str] = None):
        self.base_url = (base_url or getattr(settings, "INFERENCE_SERVICE_URL", "http://127.0.0.1:8001")).rstrip("/")
        self.timeout = timeout or getattr(settings, "INFERENCE_TIMEOUT_SECONDS", 10)
        self.service_token = service_token if service_token is not None else getattr(settings, "INFERENCE_SERVICE_TOKEN", "")

    def _build_headers(self, request_id: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.service_token:
            headers["X-Service-Token"] = self.service_token
        if request_id:
            headers["X-Request-ID"] = request_id
        return headers

    def check_liveness(self) -> Dict[str, Any]:
        """Query liveness endpoint of the inference service."""
        url = f"{self.base_url}/health/live"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Inference service liveness check failed: %s", e)
            raise InferenceClientError(
                message="Inference service liveness probe failed.",
                status_code=503,
                code="INFERENCE_UNAVAILABLE",
            )

    def check_readiness(self) -> Dict[str, Any]:
        """Query readiness endpoint of the inference service."""
        url = f"{self.base_url}/health/ready"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 503:
                data = response.json() if response.content else {}
                return {"status": "not_ready", "reason": data.get("reason", "Model not ready")}
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Inference service readiness check failed: %s", e)
            raise InferenceClientError(
                message="Inference service is currently unavailable or model is not loaded.",
                status_code=503,
                code="INFERENCE_UNAVAILABLE",
            )

    def get_model_metadata(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetch model metadata from inference service."""
        url = f"{self.base_url}/api/v1/model/metadata"
        headers = self._build_headers(request_id)
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 401 or response.status_code == 403:
                logger.error("Service authentication failure calling inference metadata: %s", response.status_code)
                raise InferenceClientError(
                    message="Internal service authentication failure with inference service.",
                    status_code=500,
                    code="SERVICE_AUTH_ERROR",
                )
            if response.status_code == 503:
                raise InferenceClientError(
                    message="Model artifact is not loaded in inference service.",
                    status_code=503,
                    code="MODEL_NOT_READY",
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error("Inference service timed out fetching metadata")
            raise InferenceClientError(
                message="Inference service timed out.",
                status_code=504,
                code="INFERENCE_TIMEOUT",
            )
        except requests.exceptions.ConnectionError:
            logger.error("Connection error to inference service")
            raise InferenceClientError(
                message="Cannot connect to inference service.",
                status_code=503,
                code="INFERENCE_UNAVAILABLE",
            )
        except requests.exceptions.RequestException as e:
            logger.error("Inference service metadata request failed: %s", e)
            raise InferenceClientError(
                message=f"Inference service error: {str(e)}",
                status_code=500,
                code="INFERENCE_ERROR",
            )

    def predict(self, property_features: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Request prediction from the independent FastAPI inference service.
        Sends correlation ID and internal service token; validates positive finite INR output.
        """
        url = f"{self.base_url}/api/v1/predict"
        req_id = request_id or str(uuid.uuid4())
        headers = self._build_headers(req_id)

        try:
            response = requests.post(url, json=property_features, headers=headers, timeout=self.timeout)

            # Handle specific status codes
            if response.status_code == 401 or response.status_code == 403:
                logger.error("Service authentication failure with inference service (req_id=%s)", req_id)
                raise InferenceClientError(
                    message="Internal service authentication failure between backend and inference service.",
                    status_code=500,
                    code="SERVICE_AUTH_ERROR",
                )
            elif response.status_code == 422:
                err_data = response.json().get("error", {})
                raise InferenceClientError(
                    message=err_data.get("message", "Validation error reported by inference service."),
                    status_code=422,
                    code=err_data.get("code", "VALIDATION_ERROR"),
                    detail=err_data.get("fields", {}),
                )
            elif response.status_code == 503:
                raise InferenceClientError(
                    message="Model artifact is not currently loaded or ready for predictions.",
                    status_code=503,
                    code="MODEL_NOT_READY",
                )
            elif response.status_code >= 500:
                err_data = response.json().get("error", {}) if response.content else {}
                raise InferenceClientError(
                    message=err_data.get("message", "Inference execution failed on remote service."),
                    status_code=500,
                    code=err_data.get("code", "INFERENCE_EXECUTION_FAILURE"),
                )

            response.raise_for_status()
            data = response.json()

            # Output sanity check: price must be positive and finite
            price = data.get("estimated_price_inr")
            if price is None or not isinstance(price, (int, float)) or price <= 0:
                logger.error("Inference service returned invalid/non-positive price: %s", price)
                raise InferenceClientError(
                    message="Inference service returned an invalid or non-positive price estimate.",
                    status_code=500,
                    code="INVALID_MODEL_OUTPUT",
                )

            return data

        except requests.exceptions.Timeout:
            logger.error("Inference service timed out during prediction (req_id=%s)", req_id)
            raise InferenceClientError(
                message="Prediction request timed out while contacting inference service.",
                status_code=504,
                code="INFERENCE_TIMEOUT",
            )
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to inference service (req_id=%s)", req_id)
            raise InferenceClientError(
                message="Inference service is unreachable or not running.",
                status_code=503,
                code="INFERENCE_UNAVAILABLE",
            )
