import math
import logging
import uuid
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from app.model import model_loader
from app.schemas.predict import PropertyPredictionRequest, PredictionResponse
from app.services.adapter import RequestAdapter

logger = logging.getLogger("inference_service.prediction")


class PredictionService:
    def predict(
        self,
        request: PropertyPredictionRequest,
        request_id: Optional[str] = None,
    ) -> PredictionResponse:
        """
        Executes property price inference using the pre-loaded scikit-learn pipeline.
        Fails safely when the artifact is absent or produces an invalid/non-positive output.
        Never fabricates or hard-codes a fallback price.
        """
        req_id = request_id or str(uuid.uuid4())

        # 1. Truthful readiness check
        if not model_loader.is_ready():
            logger.warning("Prediction rejected: model artifact not loaded (req_id=%s)", req_id)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "MODEL_NOT_READY",
                    "message": "Model artifact is not ready or has not been loaded. Cannot generate price estimate.",
                    "fields": {},
                    "request_id": req_id,
                },
            )

        # 2. Adapt request to single-row DataFrame with strict category/location checks
        try:
            df = RequestAdapter.request_to_dataframe(
                request=request,
                allowed_categories=model_loader.allowed_categories,
                raw_map=model_loader.allowed_categories_raw,
            )
        except ValueError as ve:
            err_msg = str(ve)
            if err_msg.startswith("UNSUPPORTED_LOCATION:"):
                clean_msg = err_msg.replace("UNSUPPORTED_LOCATION:", "").strip()
                logger.info("Unsupported location requested: %s (req_id=%s)", clean_msg, req_id)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": "UNSUPPORTED_LOCATION",
                        "message": clean_msg,
                        "fields": {"location": request.location},
                        "request_id": req_id,
                    },
                )
            elif err_msg.startswith("INVALID_CATEGORY:"):
                clean_msg = err_msg.replace("INVALID_CATEGORY:", "").strip()
                logger.info("Invalid category requested: %s (req_id=%s)", clean_msg, req_id)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": "INVALID_CATEGORY",
                        "message": clean_msg,
                        "fields": {},
                        "request_id": req_id,
                    },
                )
            else:
                logger.info("Request adaptation error: %s (req_id=%s)", err_msg, req_id)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": "INVALID_REQUEST_FIELD",
                        "message": err_msg,
                        "fields": {},
                        "request_id": req_id,
                    },
                )

        # 3. Call fitted pipeline predict() exactly once
        try:
            preds = model_loader.model.predict(df)
            if preds is None or len(preds) == 0:
                raise ValueError("Model returned an empty prediction array")
            raw_val = float(preds[0])
        except Exception as e:
            logger.error("Inference execution error: %s (req_id=%s)", e, req_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INFERENCE_ERROR",
                    "message": "Internal error occurred during model prediction execution.",
                    "fields": {},
                    "request_id": req_id,
                },
            )

        # 4. Output sanity checks: strictly finite and positive
        if not math.isfinite(raw_val) or raw_val <= 0:
            logger.error("Model produced invalid output %s (req_id=%s)", raw_val, req_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INVALID_MODEL_OUTPUT",
                    "message": "Model generated an invalid non-positive or non-finite price estimate.",
                    "fields": {"raw_prediction": raw_val if math.isfinite(raw_val) else "non-finite"},
                    "request_id": req_id,
                },
            )

        model_version = "unknown"
        if model_loader.metadata:
            model_version = model_loader.metadata.get("model_id", "real_estate_model_v1")

        summary = {
            "location": request.location,
            "area_value": request.area_value,
            "area_basis": request.area_basis.value,
            "bhk": request.bhk,
            "bathrooms": request.bathrooms,
            "balcony": request.balcony,
            "floor_number": request.floor_number,
            "total_floors": request.total_floors,
            "parking_spaces": request.parking_spaces,
        }

        return PredictionResponse(
            request_id=req_id,
            estimated_price_inr=round(raw_val, 2),
            currency="INR",
            model_version=model_version,
            schema_version="1.0",
            property_summary={k: v for k, v in summary.items() if v is not None},
        )


prediction_service = PredictionService()
