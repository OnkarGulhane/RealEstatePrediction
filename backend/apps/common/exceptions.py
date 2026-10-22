import uuid
import logging
from typing import Any, Dict
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied as DRFPermissionDenied,
    NotFound,
    MethodNotAllowed,
    ValidationError as DRFValidationError,
    Throttled,
)
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger("backend.exceptions")


def get_request_id(request) -> str:
    if request is not None:
        req_id = request.headers.get("X-Request-ID")
        if req_id:
            return req_id
        if hasattr(request, "_request_id"):
            return request._request_id
        generated = str(uuid.uuid4())
        request._request_id = generated
        return generated
    return str(uuid.uuid4())


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    Standardized DRF Exception Handler enforcing SRS Section 7.5 envelope:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "fields": { ... },
            "request_id": "uuid"
        }
    }
    """
    request = context.get("request")
    request_id = get_request_id(request)

    # Let DRF handle standard HTTP exceptions first
    response = exception_handler(exc, context)

    code = "INTERNAL_SERVER_ERROR"
    message = "An unexpected server error occurred."
    fields = {}

    if response is not None:
        # Determine appropriate machine-readable error code
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            code = "AUTHENTICATION_FAILED"
            message = "Authentication credentials were not provided or are invalid."
        elif isinstance(exc, (DRFPermissionDenied, PermissionDenied)):
            code = "PERMISSION_DENIED"
            message = str(exc.detail) if hasattr(exc, "detail") and exc.detail else "You do not have permission to perform this action."
        elif isinstance(exc, (NotFound, Http404)):
            code = "NOT_FOUND"
            message = "The requested resource was not found."
        elif isinstance(exc, MethodNotAllowed):
            code = "METHOD_NOT_ALLOWED"
            message = f"Method '{request.method}' is not allowed for this endpoint."
        elif isinstance(exc, Throttled):
            code = "THROTTLED"
            message = f"Request was throttled. Expected available in {exc.wait} seconds."
        elif isinstance(exc, (DRFValidationError, DjangoValidationError)):
            code = "VALIDATION_ERROR"
            message = "One or more input fields failed validation."
            if isinstance(response.data, dict):
                # Flatten or retain field mapping
                for k, v in response.data.items():
                    if k == "detail":
                        message = str(v)
                    elif k == "non_field_errors":
                        message = " ".join([str(item) for item in (v if isinstance(v, list) else [v])])
                    else:
                        fields[k] = [str(item) for item in (v if isinstance(v, list) else [v])]
            elif isinstance(response.data, list):
                message = " ".join([str(item) for item in response.data])

        # If data is a dict with explicit code/message/fields (e.g. from custom APIException)
        if isinstance(response.data, dict) and "code" in response.data and "message" in response.data:
            code = response.data.get("code", code)
            message = response.data.get("message", message)
            fields = response.data.get("fields", fields)

        response.data = {
            "error": {
                "code": code,
                "message": message,
                "fields": fields,
                "request_id": request_id,
            }
        }
        response["X-Request-ID"] = request_id
        return response

    # Unhandled 500 error
    logger.exception("Unhandled server exception (request_id=%s): %s", request_id, exc)
    res = Response(
        {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred.",
                "fields": {},
                "request_id": request_id,
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    res["X-Request-ID"] = request_id
    return res
