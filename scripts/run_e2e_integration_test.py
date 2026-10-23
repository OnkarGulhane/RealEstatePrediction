"""
GharScope End-to-End (E2E) Cross-Service Integration & Security QA Suite
Validates live coordination across:
  - Frontend: http://localhost:3000
  - Django Application Backend: http://localhost:8000/api/v1
  - FastAPI Inference Microservice: http://localhost:8001
"""

import sys
import time
import uuid
import requests

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DJANGO_BASE = "http://localhost:8000/api/v1"
FASTAPI_BASE = "http://localhost:8001"
FRONTEND_BASE = "http://localhost:3000"

PASSED = 0
FAILED = 0


def log_test(name: str, passed: bool, detail: str = ""):
    global PASSED, FAILED
    status = "PASS" if passed else "FAIL"
    if passed:
        PASSED += 1
        print(f"[{status}] {name}" + (f" -> {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"[{status}] {name}" + (f" -> {detail}" if detail else ""))


def run_e2e_suite():
    print("\n==================================================================")
    print("  GharScope Phase 6: Live E2E Integration & Security Test Suite")
    print("==================================================================\n")

    # 1. Health Probes
    try:
        r_fe = requests.get(FRONTEND_BASE, timeout=5)
        log_test("Frontend Liveness (Port 3000)", r_fe.status_code == 200, f"HTTP {r_fe.status_code}")
    except Exception as e:
        log_test("Frontend Liveness (Port 3000)", False, str(e))

    try:
        r_dj = requests.get(f"{DJANGO_BASE}/health/", timeout=5)
        log_test("Django Backend Health (Port 8000)", r_dj.status_code == 200, f"HTTP {r_dj.status_code} ({r_dj.json().get('status')})")
    except Exception as e:
        log_test("Django Backend Health (Port 8000)", False, str(e))

    try:
        r_fa = requests.get(f"{FASTAPI_BASE}/health/ready", timeout=5)
        log_test("FastAPI Inference Readiness (Port 8001)", r_fa.status_code == 200, f"HTTP {r_fa.status_code} ({r_fa.json().get('status')})")
    except Exception as e:
        log_test("FastAPI Inference Readiness (Port 8001)", False, str(e))

    # 2. Locations Metadata
    try:
        r_loc = requests.get(f"{DJANGO_BASE}/locations/", timeout=5)
        locs = r_loc.json().get("locations", [])
        log_test("Locations Catalog Delivery", r_loc.status_code == 200 and len(locs) >= 81, f"Found {len(locs)} micro-markets")
    except Exception as e:
        log_test("Locations Catalog Delivery", False, str(e))

    # 3. CSRF Bootstrap Handshake
    session_a = requests.Session()
    csrf_token_a = None
    try:
        r_csrf = session_a.get(f"{DJANGO_BASE}/auth/csrf/", timeout=5)
        csrf_token_a = r_csrf.json().get("csrf_token") or r_csrf.cookies.get("csrftoken")
        has_cookie = "csrftoken" in session_a.cookies
        log_test("CSRF Handshake & Cookie Bootstrap", r_csrf.status_code == 200 and bool(csrf_token_a) and has_cookie, f"Cookie set: {has_cookie}")
    except Exception as e:
        log_test("CSRF Handshake & Cookie Bootstrap", False, str(e))

    # 4. User Registration (User A)
    user_a_email = f"e2e_buyer_{int(time.time())}_{uuid.uuid4().hex[:4]}@gharscope.com"
    user_a_password = "P@ssword123Secure!"
    user_a_name = "Aditi Sharma"
    try:
        r_reg = session_a.post(
            f"{DJANGO_BASE}/auth/register/",
            json={"email": user_a_email, "password": user_a_password, "display_name": user_a_name},
            headers={"X-CSRFToken": csrf_token_a or ""},
            timeout=5,
        )
        log_test("User Registration Flow", r_reg.status_code in (200, 201), f"HTTP {r_reg.status_code} ({user_a_email})")
    except Exception as e:
        log_test("User Registration Flow", False, str(e))

    # 5. User Login (User A) -> JWT Access Token + HttpOnly Refresh Cookie
    access_token_a = None
    try:
        r_login = session_a.post(
            f"{DJANGO_BASE}/auth/login/",
            json={"email": user_a_email, "password": user_a_password},
            headers={"X-CSRFToken": csrf_token_a or ""},
            timeout=5,
        )
        data_login = r_login.json()
        access_token_a = data_login.get("access")
        has_refresh_cookie = "refresh_token" in session_a.cookies
        log_test("User Login & SimpleJWT Issuance", r_login.status_code == 200 and bool(access_token_a), f"Access token received, refresh cookie: {has_refresh_cookie}")
    except Exception as e:
        log_test("User Login & SimpleJWT Issuance", False, str(e))

    # 6. Authenticated Profile Hydration (/auth/me/)
    try:
        r_me = session_a.get(
            f"{DJANGO_BASE}/auth/me/",
            headers={"Authorization": f"Bearer {access_token_a}"},
            timeout=5,
        )
        me_data = r_me.json()
        log_test("User Profile Hydration (/auth/me/)", r_me.status_code == 200 and me_data.get("email") == user_a_email, f"User: {me_data.get('display_name')}")
    except Exception as e:
        log_test("User Profile Hydration (/auth/me/)", False, str(e))

    # 7. End-to-End Property Valuation Submission
    # Frontend -> Django POST /predictions/ -> FastAPI POST /predict -> LightGBM -> DB Persistence -> Response
    prediction_id = None
    predicted_inr = None
    try:
        payload = {
            "schema_version": "1.0",
            "location": "Bangalore",
            "area_value": 1450.0,
            "area_basis": "CARPET",
            "bhk": 3,
            "bathrooms": 3,
            "balcony": 1,
            "parking_spaces": 1,
            "floor_number": 4,
            "total_floors": 12,
            "furnishing": "Semi-Furnished",
            "transaction_type": "Resale",
            "status": "Ready to Move",
            "facing": "East",
            "ownership": "Freehold",
        }
        t0 = time.time()
        r_pred = session_a.post(
            f"{DJANGO_BASE}/predictions/",
            json=payload,
            headers={"Authorization": f"Bearer {access_token_a}"},
            timeout=8,
        )
        elapsed = (time.time() - t0) * 1000
        pred_data = r_pred.json()
        prediction_id = pred_data.get("id")
        estimated_inr = pred_data.get("estimated_price_inr")
        estimated_val = float(estimated_inr) if estimated_inr is not None else 0.0
        log_test(
            "End-to-End ML Valuation Pipeline (Frontend->Django->FastAPI->DB)",
            r_pred.status_code == 201 and estimated_val > 0,
            f"Estimated: INR {estimated_val:,.0f} in {elapsed:.1f}ms (ID: {prediction_id})",
        )
    except Exception as e:
        log_test("End-to-End ML Valuation Pipeline (Frontend->Django->FastAPI->DB)", False, str(e))

    # 8. Prediction History Listing
    try:
        r_hist = session_a.get(
            f"{DJANGO_BASE}/predictions/",
            headers={"Authorization": f"Bearer {access_token_a}"},
            timeout=5,
        )
        hist_items = r_hist.json().get("results", [])
        found_in_hist = any(item.get("id") == prediction_id for item in hist_items)
        log_test("User Prediction History Persistence", r_hist.status_code == 200 and found_in_hist, f"Found {len(hist_items)} history items")
    except Exception as e:
        log_test("User Prediction History Persistence", False, str(e))

    # 9. Single Prediction Detail Retrieval
    if prediction_id:
        try:
            r_detail = session_a.get(
                f"{DJANGO_BASE}/predictions/{prediction_id}/",
                headers={"Authorization": f"Bearer {access_token_a}"},
                timeout=5,
            )
            detail_data = r_detail.json()
            loc_found = detail_data.get("property_summary", {}).get("location")
            matches_location = loc_found == "Bangalore"
            log_test("Single Prediction Detail Query", r_detail.status_code == 200 and matches_location, f"Location verified: {loc_found}")
        except Exception as e:
            log_test("Single Prediction Detail Query", False, str(e))

    # 10. Data Isolation & Security Boundary (User B cannot see User A's prediction)
    session_b = requests.Session()
    user_b_email = f"e2e_intruder_{int(time.time())}_{uuid.uuid4().hex[:4]}@gharscope.com"
    try:
        session_b.get(f"{DJANGO_BASE}/auth/csrf/")
        csrf_b = session_b.cookies.get("csrftoken")
        session_b.post(
            f"{DJANGO_BASE}/auth/register/",
            json={"email": user_b_email, "password": "UserBPassword!123", "display_name": "Rohan Verma"},
            headers={"X-CSRFToken": csrf_b or ""},
            timeout=5,
        )
        r_login_b = session_b.post(
            f"{DJANGO_BASE}/auth/login/",
            json={"email": user_b_email, "password": "UserBPassword!123"},
            headers={"X-CSRFToken": csrf_b or ""},
            timeout=5,
        )
        access_token_b = r_login_b.json().get("access")

        # User B attempts to access User A's prediction
        r_isolation = session_b.get(
            f"{DJANGO_BASE}/predictions/{prediction_id}/",
            headers={"Authorization": f"Bearer {access_token_b}"},
            timeout=5,
        )
        # Expect 404 Not Found (strict multi-tenant isolation, no existence disclosure)
        log_test("Cross-User Privacy & Data Isolation", r_isolation.status_code == 404, f"Status code: {r_isolation.status_code} (User B denied access to User A's prediction)")
    except Exception as e:
        log_test("Cross-User Privacy & Data Isolation", False, str(e))

    # 11. Role-Based Access Control (Non-Admin denied access to /admin/)
    try:
        r_admin = session_a.get(
            f"{DJANGO_BASE}/admin/summary/",
            headers={"Authorization": f"Bearer {access_token_a}"},
            timeout=5,
        )
        log_test("RBAC Security Guard (Non-Admin /admin/ rejection)", r_admin.status_code == 403, f"Status: {r_admin.status_code} Forbidden")
    except Exception as e:
        log_test("RBAC Security Guard (Non-Admin /admin/ rejection)", False, str(e))

    # 12. Input Validation & Error Envelope (Negative Input)
    try:
        bad_payload = {
            "schema_version": "1.0",
            "location": "NonExistentCity",
            "area_value": -500.0,  # Negative area
            "area_basis": "INVALID_BASIS",
        }
        r_bad = session_a.post(
            f"{DJANGO_BASE}/predictions/",
            json=bad_payload,
            headers={"Authorization": f"Bearer {access_token_a}"},
            timeout=5,
        )
        err_json = r_bad.json()
        is_rfc7807 = "error" in err_json and "code" in err_json.get("error", {})
        log_test("Contract Validation & RFC 7807 Error Shape", r_bad.status_code == 400 and is_rfc7807, f"Error Code: {err_json.get('error', {}).get('code')}")
    except Exception as e:
        log_test("Contract Validation & RFC 7807 Error Shape", False, str(e))

    # 13. Token Refresh Flow
    try:
        r_refresh = session_a.post(
            f"{DJANGO_BASE}/auth/refresh/",
            headers={"X-CSRFToken": csrf_token_a or ""},
            timeout=5,
        )
        new_access = r_refresh.json().get("access")
        log_test("JWT Token Refresh Handshake", r_refresh.status_code == 200 and bool(new_access), "New access token received via refresh cookie")
    except Exception as e:
        log_test("JWT Token Refresh Handshake", False, str(e))

    # 14. User Logout & Cookie Revocation
    try:
        r_logout = session_a.post(
            f"{DJANGO_BASE}/auth/logout/",
            headers={"Authorization": f"Bearer {access_token_a}", "X-CSRFToken": csrf_token_a or ""},
            timeout=5,
        )
        log_test("User Logout & Session Blacklisting", r_logout.status_code in (200, 204), f"HTTP {r_logout.status_code}")
    except Exception as e:
        log_test("User Logout & Session Blacklisting", False, str(e))

    print("\n------------------------------------------------------------------")
    print(f"  Phase 6 E2E Integration Suite Summary: {PASSED} Passed, {FAILED} Failed")
    print("------------------------------------------------------------------\n")
    return FAILED == 0


if __name__ == "__main__":
    success = run_e2e_suite()
    sys.exit(0 if success else 1)
