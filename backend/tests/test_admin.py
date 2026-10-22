import pytest
from unittest.mock import patch
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.predictions.models import Prediction

User = get_user_model()


@pytest.mark.django_db
class TestAdminEndpoints:
    def setup_method(self):
        self.anon_client = APIClient()

        # Regular user
        self.user = User.objects.create_user(
            email="regular@example.com",
            password="StrongPassword123!",
            display_name="Regular User",
        )
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)

        # Admin user
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="AdminPassword123!",
            display_name="Admin User",
            is_staff=True,
        )
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

        # Seed test predictions
        self.pred1 = Prediction.objects.create(
            user=self.user,
            schema_version="1.0",
            location="Mumbai",
            area_value=1200.0,
            area_basis="CARPET",
            bhk=3,
            bathrooms=3,
            parking_spaces=1,
            estimated_price_inr=Decimal("15000000.00"),
            currency="INR",
            model_version="1.0.0",
        )
        self.pred2 = Prediction.objects.create(
            user=self.admin_user,
            schema_version="1.0",
            location="Pune",
            area_value=900.0,
            area_basis="SUPER",
            bhk=2,
            bathrooms=2,
            parking_spaces=1,
            estimated_price_inr=Decimal("7500000.00"),
            currency="INR",
            model_version="1.0.0",
        )

    def test_permission_gates_for_all_admin_endpoints(self):
        admin_urls = [
            "/api/v1/admin/summary/",
            "/api/v1/admin/users/",
            "/api/v1/admin/predictions/",
            "/api/v1/admin/reports/",
            "/api/v1/admin/model/",
        ]
        for url in admin_urls:
            # Anonymous request must fail with 401
            resp_anon = self.anon_client.get(url)
            assert resp_anon.status_code == status.HTTP_401_UNAUTHORIZED, f"Expected 401 for anon at {url}"

            # Non-staff user must fail with 403
            resp_user = self.user_client.get(url)
            assert resp_user.status_code == status.HTTP_403_FORBIDDEN, f"Expected 403 for non-admin at {url}"

    def test_admin_summary(self):
        resp = self.admin_client.get("/api/v1/admin/summary/")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()

        assert "users" in data
        assert data["users"]["total"] == 2
        assert data["users"]["staff"] == 1
        assert data["users"]["active"] == 2

        assert "predictions" in data
        assert data["predictions"]["total"] == 2
        assert data["predictions"]["total_volume_inr"] == 22500000.00
        assert data["predictions"]["average_price_inr"] == 11250000.00
        assert data["currency"] == "INR"
        assert "server_time" in data

    def test_admin_users_list_and_search(self):
        resp = self.admin_client.get("/api/v1/admin/users/")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()

        assert "results" in data
        assert data["count"] == 2
        user_emails = [u["email"] for u in data["results"]]
        assert "regular@example.com" in user_emails
        assert "admin@example.com" in user_emails

        # Search filter
        resp_search = self.admin_client.get("/api/v1/admin/users/?search=regular")
        assert resp_search.status_code == status.HTTP_200_OK
        search_data = resp_search.json()
        assert search_data["count"] == 1
        assert search_data["results"][0]["email"] == "regular@example.com"
        assert search_data["results"][0]["prediction_count"] == 1

    def test_admin_predictions_list_and_filters(self):
        resp = self.admin_client.get("/api/v1/admin/predictions/")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["count"] == 2

        # Filter by location
        resp_mumbai = self.admin_client.get("/api/v1/admin/predictions/?location=Mumbai")
        assert resp_mumbai.status_code == status.HTTP_200_OK
        mumbai_data = resp_mumbai.json()
        assert mumbai_data["count"] == 1
        assert mumbai_data["results"][0]["location"] == "Mumbai"

        # Filter by area_basis
        resp_super = self.admin_client.get("/api/v1/admin/predictions/?area_basis=SUPER")
        assert resp_super.status_code == status.HTTP_200_OK
        super_data = resp_super.json()
        assert super_data["count"] == 1
        assert super_data["results"][0]["area_basis"] == "SUPER"

        # Filter by user_id
        resp_uid = self.admin_client.get(f"/api/v1/admin/predictions/?user_id={self.user.id}")
        assert resp_uid.status_code == status.HTTP_200_OK
        uid_data = resp_uid.json()
        assert uid_data["count"] == 1
        assert uid_data["results"][0]["user_email"] == "regular@example.com"

    def test_admin_reports_and_date_validation(self):
        resp = self.admin_client.get("/api/v1/admin/reports/")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()

        assert "period" in data
        assert "summary" in data
        assert data["summary"]["total_predictions"] == 2
        assert "top_locations" in data
        assert len(data["top_locations"]) > 0
        assert "daily" in data

        # Invalid start_date format
        bad_format = self.admin_client.get("/api/v1/admin/reports/?start_date=invalid-date")
        assert bad_format.status_code == status.HTTP_400_BAD_REQUEST

        # start_date > end_date
        inverted = self.admin_client.get("/api/v1/admin/reports/?start_date=2026-10-25&end_date=2026-10-20")
        assert inverted.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_model_metadata_live_and_fallback(self):
        # 1. Fallback when inference service is down
        with patch("apps.predictions.clients.inference_client.InferenceClient.get_model_metadata", side_effect=Exception("Connection refused")):
            resp = self.admin_client.get("/api/v1/admin/model/")
            assert resp.status_code == status.HTTP_200_OK
            data = resp.json()
            assert data["model_id"] == "real_estate_hist_gradient_boosting_log_tuned_v1"
            assert data["test_evaluation"]["holdout_r2"] == 0.7104

        # 2. Live metadata when inference client succeeds
        mock_live_meta = {
            "model_version": "1.0.0",
            "model_name": "TunedHistGradientBoosting",
            "features": ["bhk", "bathrooms"],
        }
        with patch("apps.predictions.clients.inference_client.InferenceClient.get_model_metadata", return_value=mock_live_meta):
            resp = self.admin_client.get("/api/v1/admin/model/")
            assert resp.status_code == status.HTTP_200_OK
            assert resp.json() == mock_live_meta
