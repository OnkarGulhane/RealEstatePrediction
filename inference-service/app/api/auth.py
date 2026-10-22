import secrets
import uuid
from typing import Optional
from fastapi import Header, HTTPException, Request, status
from app.config import settings


def verify_service_token(
    request: Request,
    x_service_token: Optional[str] = Header(None, alias="X-Service-Token"),
) -> None:
    """
    Validates the internal service authentication token.
    Uses constant-time comparison (secrets.compare_digest) and never logs the secret.
    If SERVICE_TOKEN is configured in settings:
      - Missing header -> 401 Unauthorized
      - Invalid token -> 403 Forbidden
    """
    configured_token = settings.SERVICE_TOKEN
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if configured_token and configured_token.strip():
        if not x_service_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED",
                    "message": "Missing required 'X-Service-Token' header for internal service access.",
                    "fields": {},
                    "request_id": req_id,
                },
            )
        if not secrets.compare_digest(x_service_token.strip(), configured_token.strip()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Invalid service authentication credential.",
                    "fields": {},
                    "request_id": req_id,
                },
            )
