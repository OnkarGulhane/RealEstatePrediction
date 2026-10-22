import pytest
from unittest.mock import patch, MagicMock
import requests
from apps.predictions.clients.inference_client import InferenceClient, InferenceClientError


class TestInferenceClient:
    def setup_method(self):
        self.client = InferenceClient(
            base_url="http://127.0.0.1:8001",
            timeout=5,
            service_token="test-secret-token",
        )

    def test_headers_construction(self):
        headers = self.client._build_headers(request_id="req-12345")
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert headers["X-Service-Token"] == "test-secret-token"
        assert headers["X-Request-ID"] == "req-12345"

    @patch("requests.get")
    def test_check_liveness_success_and_failure(self, mock_get):
        # Success
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_resp

        res = self.client.check_liveness()
        assert res == {"status": "ok"}

        # Failure
        mock_get.side_effect = requests.exceptions.ConnectionError("refused")
        with pytest.raises(InferenceClientError) as exc_info:
            self.client.check_liveness()
        assert exc_info.value.status_code == 503
        assert exc_info.value.code == "INFERENCE_UNAVAILABLE"

    @patch("requests.get")
    def test_check_readiness(self, mock_get):
        # Ready
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ready"}
        mock_get.return_value = mock_resp

        res = self.client.check_readiness()
        assert res == {"status": "ready"}

        # 503 unready
        mock_resp_503 = MagicMock()
        mock_resp_503.status_code = 503
        mock_resp_503.content = b'{"status": "not_ready", "reason": "model loading"}'
        mock_resp_503.json.return_value = {"status": "not_ready", "reason": "model loading"}
        mock_get.return_value = mock_resp_503

        res_unready = self.client.check_readiness()
        assert res_unready["status"] == "not_ready"
        assert res_unready["reason"] == "model loading"

    @patch("requests.get")
    def test_get_model_metadata(self, mock_get):
        # Success
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"model_name": "TunedHistGradientBoosting"}
        mock_get.return_value = mock_resp

        data = self.client.get_model_metadata(request_id="req-1")
        assert data["model_name"] == "TunedHistGradientBoosting"

        # Service auth error (401)
        mock_resp_401 = MagicMock()
        mock_resp_401.status_code = 401
        mock_get.return_value = mock_resp_401
        with pytest.raises(InferenceClientError) as exc:
            self.client.get_model_metadata()
        assert exc.value.code == "SERVICE_AUTH_ERROR"

        # Timeout
        mock_get.side_effect = requests.exceptions.Timeout("timed out")
        with pytest.raises(InferenceClientError) as exc:
            self.client.get_model_metadata()
        assert exc.value.code == "INFERENCE_TIMEOUT"
        assert exc.value.status_code == 504

    @patch("requests.post")
    def test_predict_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "estimated_price_inr": 8500000.0,
            "currency": "INR",
            "model_version": "1.0.0",
            "schema_version": "1.0",
        }
        mock_post.return_value = mock_resp

        payload = {"location": "Mumbai", "area_value": 1000.0, "area_basis": "CARPET"}
        result = self.client.predict(payload, request_id="corr-123")
        assert result["estimated_price_inr"] == 8500000.0

    @patch("requests.post")
    def test_predict_rejects_negative_or_zero_price(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "estimated_price_inr": -100.0,
            "currency": "INR",
        }
        mock_post.return_value = mock_resp

        with pytest.raises(InferenceClientError) as exc:
            self.client.predict({"location": "Pune", "area_value": 500.0, "area_basis": "CARPET"})
        assert exc.value.code == "INVALID_MODEL_OUTPUT"
        assert exc.value.status_code == 500

    @patch("requests.post")
    def test_predict_validation_error_from_inference(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 422
        mock_resp.json.return_value = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request fields",
                "fields": {"area_value": "Value must be positive"},
            }
        }
        mock_post.return_value = mock_resp

        with pytest.raises(InferenceClientError) as exc:
            self.client.predict({"location": "Pune", "area_value": -50.0, "area_basis": "CARPET"})
        assert exc.value.code == "VALIDATION_ERROR"
        assert exc.value.status_code == 422
        assert "area_value" in exc.value.detail
