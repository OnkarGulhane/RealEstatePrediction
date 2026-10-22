import logging
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserProfileUpdateSerializer,
)

logger = logging.getLogger("backend.accounts")


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    cookie_name = getattr(settings, "AUTH_COOKIE_REFRESH", "refresh_token")
    path = getattr(settings, "AUTH_COOKIE_PATH", "/api/v1/auth/")
    secure = getattr(settings, "AUTH_COOKIE_SECURE", False)
    samesite = getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax")
    max_age = 7 * 24 * 3600  # 7 days

    response.set_cookie(
        key=cookie_name,
        value=refresh_token,
        max_age=max_age,
        httponly=True,
        samesite=samesite,
        secure=secure,
        path=path,
    )


def clear_refresh_cookie(response: Response) -> None:
    cookie_name = getattr(settings, "AUTH_COOKIE_REFRESH", "refresh_token")
    path = getattr(settings, "AUTH_COOKIE_PATH", "/api/v1/auth/")
    response.delete_cookie(key=cookie_name, path=path)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info("New user registered successfully: %s", user.email)
        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "User registered successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = data["user"]
        access_token = data["access"]
        refresh_token = data["refresh"]

        response = Response(
            {
                "access": access_token,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, refresh_token)
        logger.info("User logged in successfully: %s", user.email)
        return response


from django.middleware.csrf import get_token
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

def enforce_csrf(request) -> None:
    """
    Enforce Django CSRF validation for cookie-backed state-changing requests.
    Uses DRF's standard CSRFCheck (subclass of CsrfViewMiddleware).
    """
    def dummy_get_response(req):
        return None

    check = CSRFCheck(dummy_get_response)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        logger.warning("CSRF validation failed on endpoint %s: %s", request.path, reason)
        raise PermissionDenied(f"CSRF verification failed: {reason}")


class CsrfTokenView(APIView):
    """
    Public CSRF token bootstrap endpoint for Next.js / SPA clients.
    Returns a masked CSRF token in JSON and sets the csrftoken cookie.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = get_token(request)
        response = Response({"csrf_token": token}, status=status.HTTP_200_OK)
        cookie_name = getattr(settings, "CSRF_COOKIE_NAME", "csrftoken")
        response.set_cookie(
            key=cookie_name,
            value=token,
            max_age=getattr(settings, "CSRF_COOKIE_AGE", 31449600),
            path=getattr(settings, "CSRF_COOKIE_PATH", "/"),
            domain=getattr(settings, "CSRF_COOKIE_DOMAIN", None),
            secure=getattr(settings, "CSRF_COOKIE_SECURE", False),
            httponly=getattr(settings, "CSRF_COOKIE_HTTPONLY", False),
            samesite=getattr(settings, "CSRF_COOKIE_SAMESITE", "Lax"),
        )
        return response


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cookie_name = getattr(settings, "AUTH_COOKIE_REFRESH", "refresh_token")
        has_cookie = cookie_name in request.COOKIES

        # Mandatory CSRF validation if request relies on ambient refresh cookie
        # (even if a JSON body token is also sent; no bypass)
        if has_cookie:
            enforce_csrf(request)

        refresh_token = request.COOKIES.get(cookie_name) or request.data.get("refresh")
        if not refresh_token:
            raise AuthenticationFailed("Refresh token is required.")

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, ValidationError) as e:
            msg = str(e.detail) if hasattr(e, "detail") else str(e)
            clear_res = Response(
                {"error": {"code": "TOKEN_INVALID", "message": msg, "fields": {}, "request_id": ""}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_refresh_cookie(clear_res)
            return clear_res

        data = serializer.validated_data
        response = Response({"access": data["access"]}, status=status.HTTP_200_OK)
        if "refresh" in data:
            set_refresh_cookie(response, data["refresh"])
        return response


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cookie_name = getattr(settings, "AUTH_COOKIE_REFRESH", "refresh_token")
        has_cookie = cookie_name in request.COOKIES

        # Enforce CSRF if using ambient cookie
        if has_cookie:
            enforce_csrf(request)

        refresh_token = request.COOKIES.get(cookie_name) or request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass  # Token already blacklisted or expired

        response = Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        clear_refresh_cookie(response)
        return response


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        # Normal users can only update allowed profile fields (e.g. display_name)
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)
