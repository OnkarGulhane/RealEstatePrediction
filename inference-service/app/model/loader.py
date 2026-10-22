import os
from pathlib import Path
from typing import Optional, Any
from app.config import settings

class ModelLoader:
    def __init__(self):
        self._model: Optional[Any] = None
        self._metadata: Optional[dict] = None

    def is_ready(self) -> bool:
        """
        Truthfully checks whether an approved model artifact exists on disk.
        Does not pretend or fabricate readiness if file is missing.
        """
        artifact_path = Path(settings.MODEL_ARTIFACT_PATH)
        return artifact_path.exists() and self._model is not None

    def load_artifact(self) -> bool:
        """
        Attempts to load the serialized pipeline artifact at application startup.
        In scaffold state, if artifact does not exist, marks service as not ready.
        """
        artifact_path = Path(settings.MODEL_ARTIFACT_PATH)
        if not artifact_path.exists():
            self._model = None
            return False

        # In Phase 3, joblib loading and metadata verification will occur here
        return False

    @property
    def model(self) -> Optional[Any]:
        return self._model

    @property
    def metadata(self) -> Optional[dict]:
        return self._metadata

model_loader = ModelLoader()
