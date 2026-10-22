from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    
    # Path relative to inference-service root
    MODEL_ARTIFACT_PATH: str = os.environ.get(
        "MODEL_ARTIFACT_PATH",
        str(Path(__file__).resolve().parent.parent.parent / "artifacts" / "model_pipeline.joblib")
    )
    MODEL_METADATA_PATH: str = os.environ.get(
        "MODEL_METADATA_PATH",
        str(Path(__file__).resolve().parent.parent.parent / "artifacts" / "metadata.json")
    )

settings = Settings()
