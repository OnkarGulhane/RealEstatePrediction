import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import router
from app.model import model_loader
from app.config import settings

logger = logging.getLogger("inference_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: attempt loading approved artifact once
    logger.info("Initializing inference service lifespan: attempting model load...")
    success = model_loader.load_artifact()
    if success:
        logger.info("Model pipeline loaded and verified successfully.")
    else:
        logger.warning(
            "Model pipeline could not be loaded at startup (reason: %s). Liveness remains available; readiness will report 503.",
            model_loader.last_error,
        )
    yield
    # Shutdown logic if needed
    logger.info("Inference service shutting down.")


app = FastAPI(
    title="Real Estate Price Prediction — Inference Service",
    version="1.0.0",
    description="Standalone internal inference HTTP service for evaluating Indian residential property prices.",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = req_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    field_errors = {}
    for err in exc.errors():
        loc = ".".join(str(part) for part in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        field_errors[loc] = msg

    # Identify if schema_version or location was specific reason
    code = "VALIDATION_ERROR"
    for err in exc.errors():
        msg = err.get("msg", "")
        if "Incompatible schema version" in msg:
            code = "INCOMPATIBLE_SCHEMA_VERSION"
            break

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": code,
                "message": "The request body failed validation constraints.",
                "fields": field_errors,
                "request_id": req_id,
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    detail = exc.detail

    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        error_payload = {
            "code": detail["code"],
            "message": detail["message"],
            "fields": detail.get("fields", {}),
            "request_id": detail.get("request_id", req_id),
        }
    else:
        error_payload = {
            "code": "HTTP_ERROR",
            "message": str(detail),
            "fields": {},
            "request_id": req_id,
        }

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error_payload},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.exception("Unhandled internal exception (req_id=%s): %s", req_id, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "fields": {},
                "request_id": req_id,
            }
        },
    )


app.include_router(router)
