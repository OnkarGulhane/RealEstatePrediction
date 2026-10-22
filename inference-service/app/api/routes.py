import uuid
from typing import Dict, Any
from fastapi import APIRouter, status, Response, Request, Depends, HTTPException
from app.schemas import (
    PropertyPredictionRequest,
    PredictionResponse,
    HealthLiveResponse,
    HealthReadyResponse,
)
from app.model import model_loader
from app.services import prediction_service
from app.api.auth import verify_service_token

router = APIRouter()


@router.get(
    "/health/live",
    response_model=HealthLiveResponse,
    summary="Process Liveness Probe",
    tags=["Health"],
)
def get_liveness():
    """
    Returns process liveness independently of model readiness.
    Always returns 200 while the HTTP process is running.
    """
    return HealthLiveResponse(status="alive", service="inference-service")


@router.get(
    "/health/ready",
    response_model=HealthReadyResponse,
    summary="Model Readiness Probe",
    tags=["Health"],
)
def get_readiness(response: Response):
    """
    Truthful readiness check.
    Returns 200 only if the approved model artifact and metadata were verified and loaded.
    Returns 503 otherwise, without exposing filesystem paths or stack traces.
    """
    if model_loader.is_ready():
        model_ver = "unknown"
        if model_loader.metadata:
            model_ver = model_loader.metadata.get("model_id", "real_estate_model_v1")
        return HealthReadyResponse(
            status="ready",
            model_version=model_ver,
        )

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthReadyResponse(
        status="not_ready",
        reason=model_loader.last_error or "Model artifact not loaded or missing",
    )


@router.post(
    "/api/v1/predict",
    response_model=PredictionResponse,
    summary="Predict Residential Property Price",
    tags=["Inference"],
    dependencies=[Depends(verify_service_token)],
)
def predict_price(request: PropertyPredictionRequest, req: Request):
    """
    Evaluates input property features using the loaded pipeline artifact.
    Returns price estimate in INR. Never fabricates a fallback or placeholder price.
    Protected by internal service token when configured.
    """
    req_id = getattr(req.state, "request_id", str(uuid.uuid4()))
    return prediction_service.predict(request, request_id=req_id)


@router.get(
    "/api/v1/model/metadata",
    summary="Sanitized Model Metadata",
    tags=["Inference"],
    dependencies=[Depends(verify_service_token)],
)
def get_model_metadata(req: Request):
    """
    Returns allow-listed summary metadata of the loaded Phase 2 model.
    Strictly excludes internal local file-system paths, dataset hashes, or secrets.
    Protected by internal service token when configured.
    """
    req_id = getattr(req.state, "request_id", str(uuid.uuid4()))
    if not model_loader.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "MODEL_NOT_READY",
                "message": "No verified model artifact is currently loaded.",
                "fields": {},
                "request_id": req_id,
            },
        )
    return model_loader.get_public_metadata() or {}
