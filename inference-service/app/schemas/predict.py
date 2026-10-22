from pydantic import BaseModel, Field
from typing import Optional

class PropertyPredictionRequest(BaseModel):
    schema_version: str = Field(default="1.0", description="Contract schema version")
    location: str = Field(..., description="Supported normalized property location")
    area_value: float = Field(..., gt=0, description="Positive numeric property area")
    area_basis: str = Field(default="CARPET", description="Area basis (CARPET or SUPER)")
    bhk: Optional[int] = Field(default=None, ge=1, le=20, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(default=None, ge=1, le=20, description="Number of bathrooms")
    balcony: Optional[int] = Field(default=None, ge=0, le=10, description="Number of balconies")
    furnishing: Optional[str] = Field(default=None, description="Furnishing status")

class PredictionResponse(BaseModel):
    estimated_price_inr: float
    currency: str = "INR"
    model_version: str
    property_summary: dict
    disclaimer: str

class HealthLiveResponse(BaseModel):
    status: str = "alive"
    service: str = "inference-service"

class HealthReadyResponse(BaseModel):
    status: str
    model_version: Optional[str] = None
    reason: Optional[str] = None
