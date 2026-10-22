from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable safe error message")
    fields: Dict[str, Any] = Field(default_factory=dict, description="Field-specific error details if applicable")
    request_id: str = Field(..., description="Server-generated correlation request ID")

class ErrorResponse(BaseModel):
    error: ErrorDetail
