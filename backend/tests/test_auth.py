import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def normal_user(db):
    return User.objects.create_user(
        email="testuser@example.com",
        password="SecurePassword123!",
        display_name="Test User",
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin@example.com",
        password="AdminPassword123!",
        display_name="Admin User",
    )


@pytest.mark.django_db
class TestAuthentication:
    def test_register_creates_normal_user_successfully(self, api_client):
        url = reverse("auth-register")
        payload = {
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "display_name": "New User",
            "is_staff": True,  # Attacking privilege escalation
            "is_superuser": True,
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["display_name"] == "New User"
        assert data["user"]["is_staff"] is False  # Privilege escalation prevented

        user = User.objects.get(email="newuser@example.com")
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("StrongPassword123!") is True

    def test_register_rejects_duplicate_email_case_insensitively(self, api_client, normal_user):
        url = reverse("auth-register")
        payload = {
            "email": "TESTUSER@EXAMPLE.COM",  # Same email uppercase
            "password": "AnotherPassword123!",
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "already exists" in str(data["error"]["fields"])

    def test_register_rejects_weak_or_short_password(self, api_client):
        url = reverse("auth-register")
        payload = {
            "email": "weak@example.com",
            "password": "123",
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert "password" in data["error"]["fields"]

    def test_login_returns_access_token_and_sets_httponly_cookie(self, api_client, normal_user):
        url = reverse("auth-login")
        payload = {
            "email": "testuser@example.com",
            "password": "SecurePassword123!",
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "user" in data
        assert data["user"]["email"] == "testuser@example.com"
        assert "refresh" not in data  # Refresh token NOT in JSON response

        # Check HttpOnly cookie
        assert "refresh_token" in response.cookies
        cookie = response.cookies["refresh_token"]
        assert cookie["httponly"] is True
        assert cookie["samesite"] == "Lax"

    def test_login_fails_safely_on_invalid_credentials(self, api_client, normal_user):
        url = reverse("auth-login")
        payload = {
            "email": "testuser@example.com",
            "password": "WrongPassword999!",
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Invalid email address or password" in data["error"]["message"]
        assert "refresh_token" not in response.cookies

    def test_csrf_token_bootstrap_endpoint(self, api_client):
        url = reverse("auth-csrf")
        response = api_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert "csrf_token" in data
        assert len(data["csrf_token"]) >= 32
        assert "csrftoken" in response.cookies
        assert response.cookies["csrftoken"]["samesite"] == "Lax"

    def test_refresh_token_rotation_and_blacklisting(self, api_client, normal_user):
        refresh = RefreshToken.for_user(normal_user)
        refresh_str = str(refresh)

        # Obtain valid CSRF token
        csrf_res = api_client.get(reverse("auth-csrf"))
        csrf_token = csrf_res.json()["csrf_token"]

        # 1. Successful refresh using cookie + valid CSRF
        url = reverse("auth-refresh")
        api_client.cookies["refresh_token"] = refresh_str
        response = api_client.post(url, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh_token" in response.cookies
        new_refresh_str = response.cookies["refresh_token"].value
        assert new_refresh_str != refresh_str

        # 2. Attempt reuse of old blacklisted refresh token
        api_client.cookies["refresh_token"] = refresh_str
        response_reuse = api_client.post(url, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        assert response_reuse.status_code == 401

    def test_cookie_refresh_fails_when_csrf_token_missing(self, normal_user):
        client = APIClient(enforce_csrf_checks=True)
        refresh = RefreshToken.for_user(normal_user)
        client.cookies["refresh_token"] = str(refresh)

        url = reverse("auth-refresh")
        response = client.post(url, format="json")
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "PERMISSION_DENIED"
        assert "CSRF" in data["error"]["message"]
        assert "request_id" in data["error"]

    def test_cookie_refresh_fails_when_csrf_token_invalid(self, normal_user):
        client = APIClient(enforce_csrf_checks=True)
        # Bootstrap cookie first
        client.get(reverse("auth-csrf"))
        refresh = RefreshToken.for_user(normal_user)
        client.cookies["refresh_token"] = str(refresh)

        url = reverse("auth-refresh")
        response = client.post(url, format="json", HTTP_X_CSRFTOKEN="invalid-bogus-token-12345")
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "PERMISSION_DENIED"
        assert "CSRF" in data["error"]["message"]

    def test_cookie_refresh_succeeds_with_valid_csrf_token(self, normal_user):
        client = APIClient(enforce_csrf_checks=True)
        csrf_res = client.get(reverse("auth-csrf"))
        csrf_token = csrf_res.json()["csrf_token"]

        refresh = RefreshToken.for_user(normal_user)
        client.cookies["refresh_token"] = str(refresh)

        url = reverse("auth-refresh")
        response = client.post(url, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        assert response.status_code == 200
        assert "access" in response.json()
        assert "refresh_token" in response.cookies

    def test_cookie_logout_fails_when_csrf_token_missing(self, normal_user):
        client = APIClient(enforce_csrf_checks=True)
        refresh = RefreshToken.for_user(normal_user)
        client.cookies["refresh_token"] = str(refresh)

        url = reverse("auth-logout")
        response = client.post(url, format="json")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "PERMISSION_DENIED"

        # Token must NOT be blacklisted by failed CSRF attempt
        csrf_res = client.get(reverse("auth-csrf"))
        csrf_token = csrf_res.json()["csrf_token"]
        refresh_url = reverse("auth-refresh")
        valid_res = client.post(refresh_url, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        assert valid_res.status_code == 200

    def test_cookie_logout_fails_when_csrf_token_invalid(self, normal_user):
        client = APIClient(enforce_csrf_checks=True)
        client.get(reverse("auth-csrf"))
        refresh = RefreshToken.for_user(normal_user)
        client.cookies["refresh_token"] = str(refresh)

        url = reverse("auth-logout")
        response = client.post(url, format="json", HTTP_X_CSRFTOKEN="bogus-token")
        assert response.status_code == 403

    def test_cookie_logout_succeeds_with_valid_csrf_token(self, normal_user):
        client = APIClient(enforce_csrf_checks=True)
        csrf_res = client.get(reverse("auth-csrf"))
        csrf_token = csrf_res.json()["csrf_token"]

        refresh = RefreshToken.for_user(normal_user)
        client.cookies["refresh_token"] = str(refresh)

        url = reverse("auth-logout")
        response = client.post(url, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]

        # Next refresh attempt with blacklisted token must fail with 401
        refresh_url = reverse("auth-refresh")
        client.cookies["refresh_token"] = str(refresh)
        res_after = client.post(refresh_url, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        assert res_after.status_code == 401

    def test_json_body_refresh_without_cookie_succeeds_without_csrf(self, normal_user):
        client = APIClient(enforce_csrf_checks=True)
        refresh = RefreshToken.for_user(normal_user)

        # Pure API / mobile client sending JSON body without any cookies
        url = reverse("auth-refresh")
        response = client.post(url, {"refresh": str(refresh)}, format="json")
        assert response.status_code == 200
        assert "access" in response.json()

    def test_refresh_cookie_with_json_body_cannot_bypass_csrf(self, normal_user):
        client = APIClient(enforce_csrf_checks=True)
        refresh = RefreshToken.for_user(normal_user)
        client.cookies["refresh_token"] = str(refresh)

        # Sending JSON body while cookie is present must STILL require CSRF
        url = reverse("auth-refresh")
        response = client.post(url, {"refresh": str(refresh)}, format="json")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "PERMISSION_DENIED"

    def test_cors_credentials_headers(self, api_client):
        url = reverse("auth-csrf")

        # 1. Allowed origin in development
        res_allowed = api_client.get(url, HTTP_ORIGIN="http://localhost:3000")
        assert res_allowed.status_code == 200
        assert res_allowed.headers.get("Access-Control-Allow-Credentials") == "true"
        assert res_allowed.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"

        # 2. Unapproved origin
        res_disallowed = api_client.get(url, HTTP_ORIGIN="http://evil-attacker.com")
        assert res_disallowed.status_code == 200
        assert res_disallowed.headers.get("Access-Control-Allow-Origin") != "http://evil-attacker.com"

    def test_logout_blacklists_token_and_clears_cookie(self, api_client, normal_user):
        csrf_res = api_client.get(reverse("auth-csrf"))
        csrf_token = csrf_res.json()["csrf_token"]

        refresh = RefreshToken.for_user(normal_user)
        api_client.cookies["refresh_token"] = str(refresh)

        url = reverse("auth-logout")
        response = api_client.post(url, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]

        # Attempting refresh after logout fails
        refresh_url = reverse("auth-refresh")
        api_client.cookies["refresh_token"] = str(refresh)
        res_refresh = api_client.post(refresh_url, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        assert res_refresh.status_code == 401

    def test_current_user_profile_get_and_patch(self, api_client, normal_user):
        url = reverse("auth-me")

        # Anonymous rejected
        res_anon = api_client.get(url)
        assert res_anon.status_code == 401

        # Authenticated user
        api_client.force_authenticate(user=normal_user)
        res_get = api_client.get(url)
        assert res_get.status_code == 200
        assert res_get.json()["email"] == "testuser@example.com"

        # Update display name
        res_patch = api_client.patch(url, {"display_name": "Updated Name", "is_staff": True}, format="json")
        assert res_patch.status_code == 200
        data = res_patch.json()
        assert data["display_name"] == "Updated Name"
        assert data["is_staff"] is False  # Cannot escalate via profile patch

        normal_user.refresh_from_db()
        assert normal_user.display_name == "Updated Name"
        assert normal_user.is_staff is False
