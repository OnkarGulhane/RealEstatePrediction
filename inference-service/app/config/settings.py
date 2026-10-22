from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

SERVICE_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(SERVICE_ROOT / ".env"),
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8001

    # Paths relative to inference-service root, or absolute
    MODEL_ARTIFACT_PATH: str = "../ml/training/experiments/phase2/model_pipeline.joblib"
    MODEL_METADATA_PATH: str = "../ml/training/experiments/phase2/metadata.json"

    # Internal service authentication token
    SERVICE_TOKEN: Optional[str] = None

    @property
    def resolved_artifact_path(self) -> Path:
        p = Path(self.MODEL_ARTIFACT_PATH)
        if p.is_absolute():
            return p
        return (SERVICE_ROOT / p).resolve()

    @property
    def resolved_metadata_path(self) -> Path:
        p = Path(self.MODEL_METADATA_PATH)
        if p.is_absolute():
            return p
        return (SERVICE_ROOT / p).resolve()

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.ENVIRONMENT.lower() == "production":
            if not self.SERVICE_TOKEN or not self.SERVICE_TOKEN.strip():
                raise ValueError(
                    "SERVICE_TOKEN must be configured and non-empty when ENVIRONMENT=production."
                )
        return self

settings = Settings()
