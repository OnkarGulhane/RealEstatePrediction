from fastapi import APIRouter, status, Response
from app.schemas import (
    PropertyPredictionRequest,
    HealthLiveResponse,
    HealthReadyResponse,
)
from app.model import model_loader
from app.services import prediction_service

router = APIRouter()

@router.get("/health/live", response_model=HealthLiveResponse)
def get_liveness():
    """Returns process liveness independently of model readiness."""
    return HealthLiveResponse(status="alive", service="inference-service")

@router.get("/health/ready", response_model=HealthReadyResponse)
def get_readiness(response: Response):
    """
    Truthful readiness check.
    If no verified model artifact is loaded, sets status code to 503.
    """
    if model_loader.is_ready():
        return HealthReadyResponse(
            status="ready",
            model_version=getattr(model_loader.metadata, "get", lambda k, d=None: "v1.0.0")("model_version", "v1.0.0"),
        )
    
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthReadyResponse(
        status="not_ready",
        reason="Model artifact not loaded or missing"
    )

@router.post("/api/v1/predict")
def predict_price(request: PropertyPredictionRequest):
    """
    Predicts property price.
    In scaffold state, returns 503 Service Unavailable since model is not loaded.
    """
    return prediction_service.predict(request)

@router.get("/api/v1/model/metadata")
def get_model_metadata(response: Response):
    """Returns metadata for the currently loaded model version."""
    if not model_loader.is_ready():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "reason": "No model artifact loaded"}
    return model_loader.metadata or {}
