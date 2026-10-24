import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from apps.predictions.models import Prediction
from apps.predictions.clients.inference_client import InferenceClientError

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_a(db):
    return User.objects.create_user(email="usera@example.com", password="Password123!")


@pytest.fixture
def user_b(db):
    return User.objects.create_user(email="userb@example.com", password="Password123!")


@pytest.fixture
def valid_payload():
    return {
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


@pytest.mark.django_db
class TestPredictions:
    def test_anonymous_request_rejected(self, api_client, valid_payload):
        url = reverse("prediction-list-create")
        res_post = api_client.post(url, valid_payload, format="json")
        assert res_post.status_code == 401

        res_get = api_client.get(url)
        assert res_get.status_code == 401

    @patch("apps.predictions.views.InferenceClient.predict")
    def test_prediction_success_persists_record_and_returns_201(
        self, mock_predict, api_client, user_a, valid_payload
    ):
        mock_predict.return_value = {
            "estimated_price_inr": 8316392.49,
            "currency": "INR",
            "model_version": "real_estate_hist_gradient_boosting_log_tuned_v1",
            "schema_version": "1.0",
        }

        api_client.force_authenticate(user=user_a)
        url = reverse("prediction-list-create")
        response = api_client.post(url, valid_payload, format="json")

        assert response.status_code == 201
        data = response.json()
        assert data["estimated_price_inr"] == "8316392.49"
        assert data["currency"] == "INR"
        assert data["model_version"] == "real_estate_hist_gradient_boosting_log_tuned_v1"
        assert "id" in data
        assert "property_summary" in data
        assert data["property_summary"]["location"] == "Thane"
        assert "disclaimer" in data

        # Verify DB persistence
        assert Prediction.objects.count() == 1
        db_record = Prediction.objects.first()
        assert db_record.user == user_a
        assert float(db_record.estimated_price_inr) == 8316392.49

    @patch("apps.predictions.views.InferenceClient.predict")
    def test_prediction_with_sub_area_persists_and_returns(
        self, mock_predict, api_client, user_a, valid_payload
    ):
        mock_predict.return_value = {
            "estimated_price_inr": 9200000.00,
            "currency": "INR",
            "model_version": "real_estate_hist_gradient_boosting_log_tuned_v1",
            "schema_version": "1.0",
        }
        payload = dict(valid_payload)
        payload["location"] = "Pune"
        payload["sub_area"] = "Kothrud"

        api_client.force_authenticate(user=user_a)
        url = reverse("prediction-list-create")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == 201
        data = response.json()
        assert data["property_summary"]["location"] == "Pune"
        assert data["property_summary"]["sub_area"] == "Kothrud"

        db_rec = Prediction.objects.get(id=data["id"])
        assert db_rec.location == "Pune"
        assert db_rec.sub_area == "Kothrud"

    def test_prediction_rejects_missing_required_fields(self, api_client, user_a):
        api_client.force_authenticate(user=user_a)
        url = reverse("prediction-list-create")

        # Missing schema_version
        payload_no_schema = {
            "location": "Thane",
            "area_value": 1200.0,
            "area_basis": "CARPET",
        }
        res = api_client.post(url, payload_no_schema, format="json")
        assert res.status_code == 400
        assert "schema_version" in res.json()["error"]["fields"]

        # Incompatible schema_version != "1.0"
        payload_bad_schema = {
            "schema_version": "2.0",
            "location": "Thane",
            "area_value": 1200.0,
            "area_basis": "CARPET",
        }
        res = api_client.post(url, payload_bad_schema, format="json")
        assert res.status_code == 400
        assert "Incompatible schema version" in str(res.json())

        # Missing area_basis
        payload_no_basis = {
            "schema_version": "1.0",
            "location": "Thane",
            "area_value": 1200.0,
        }
        res = api_client.post(url, payload_no_basis, format="json")
        assert res.status_code == 400
        assert "area_basis" in res.json()["error"]["fields"]

        # Negative area_value
        payload_bad_area = {
            "schema_version": "1.0",
            "location": "Thane",
            "area_value": -500.0,
            "area_basis": "CARPET",
        }
        res = api_client.post(url, payload_bad_area, format="json")
        assert res.status_code == 400
        assert "area_value" in res.json()["error"]["fields"]

        # Invalid floor relationship: floor_number > total_floors
        payload_bad_floors = {
            "schema_version": "1.0",
            "location": "Thane",
            "area_value": 1200.0,
            "area_basis": "CARPET",
            "floor_number": 10.0,
            "total_floors": 4.0,
        }
        res = api_client.post(url, payload_bad_floors, format="json")
        assert res.status_code == 400
        assert "floor_number" in str(res.json())

        # No records should be created
        assert Prediction.objects.count() == 0

    @patch("apps.predictions.views.InferenceClient.predict")
    def test_inference_service_timeout_handling(self, mock_predict, api_client, user_a, valid_payload):
        mock_predict.side_effect = InferenceClientError(
            message="Prediction request timed out.",
            status_code=504,
            code="INFERENCE_TIMEOUT",
        )

        api_client.force_authenticate(user=user_a)
        url = reverse("prediction-list-create")
        response = api_client.post(url, valid_payload, format="json")

        assert response.status_code == 504
        data = response.json()
        assert data["error"]["code"] == "INFERENCE_TIMEOUT"
        assert Prediction.objects.count() == 0

    @patch("apps.predictions.views.InferenceClient.predict")
    def test_inference_service_unavailable_handling(self, mock_predict, api_client, user_a, valid_payload):
        mock_predict.side_effect = InferenceClientError(
            message="Cannot connect to inference service.",
            status_code=503,
            code="INFERENCE_UNAVAILABLE",
        )

        api_client.force_authenticate(user=user_a)
        url = reverse("prediction-list-create")
        response = api_client.post(url, valid_payload, format="json")

        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "INFERENCE_UNAVAILABLE"
        assert Prediction.objects.count() == 0

    @patch("apps.predictions.views.InferenceClient.predict")
    def test_user_history_and_ownership_isolation(self, mock_predict, api_client, user_a, user_b, valid_payload):
        mock_predict.return_value = {
            "estimated_price_inr": 5000000.0,
            "currency": "INR",
            "model_version": "v1",
            "schema_version": "1.0",
        }

        # User A creates 2 predictions
        api_client.force_authenticate(user=user_a)
        url = reverse("prediction-list-create")
        res_a1 = api_client.post(url, valid_payload, format="json")
        res_a2 = api_client.post(url, valid_payload, format="json")
        pred_a1_id = res_a1.json()["id"]

        # User B creates 1 prediction
        api_client.force_authenticate(user=user_b)
        res_b1 = api_client.post(url, valid_payload, format="json")
        pred_b1_id = res_b1.json()["id"]

        assert Prediction.objects.count() == 3

        # User A lists history: receives only their 2 predictions
        api_client.force_authenticate(user=user_a)
        res_history_a = api_client.get(url)
        assert res_history_a.status_code == 200
        data_a = res_history_a.json()
        assert data_a["count"] == 2
        returned_ids_a = [item["id"] for item in data_a["results"]]
        assert pred_a1_id in returned_ids_a
        assert pred_b1_id not in returned_ids_a

        # User A tries to view User B's prediction by ID -> 404 Not Found (privacy-safe)
        detail_b_url = reverse("prediction-detail", kwargs={"pk": pred_b1_id})
        res_detail_b = api_client.get(detail_b_url)
        assert res_detail_b.status_code == 404

        # User A views their own prediction -> 200 OK
        detail_a_url = reverse("prediction-detail", kwargs={"pk": pred_a1_id})
        res_detail_a = api_client.get(detail_a_url)
        assert res_detail_a.status_code == 200
        assert res_detail_a.json()["id"] == pred_a1_id
