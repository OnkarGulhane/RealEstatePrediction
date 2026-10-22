from app.model import model_loader
from app.schemas import PropertyPredictionRequest
from fastapi import HTTPException, status

class PredictionService:
    def predict(self, request: PropertyPredictionRequest) -> dict:
        """
        Executes inference using the pre-loaded pipeline model.
        In scaffold state (when model is not loaded), returns HTTP 503 Service Unavailable.
        Never fabricates or hard-codes a fake price.
        """
        if not model_loader.is_ready():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model artifact is not ready or has not been loaded. Cannot generate price estimate."
            )
        
        # In Phase 3, features will be passed to model_loader.model.predict()
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Inference logic is planned for Phase 3 implementation."
        )

prediction_service = PredictionService()
