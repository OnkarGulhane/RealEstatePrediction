import json
import logging
import threading
import sys
from pathlib import Path
from typing import Optional, Any, Dict, Set, Tuple
import joblib

from app.config import settings, SERVICE_ROOT

# Ensure real_estate_ml_training is importable for pipeline unpickling
try:
    import real_estate_ml_training  # noqa: F401
except ImportError:
    repo_root = SERVICE_ROOT.parent
    training_src = repo_root / "ml" / "training" / "src"
    if training_src.exists() and str(training_src) not in sys.path:
        sys.path.insert(0, str(training_src))

logger = logging.getLogger("inference_service.model_loader")

APPROVED_MODEL_FEATURES = [
    "carpet_area_sqft",
    "super_area_sqft",
    "has_carpet_area",
    "carpet_area_unit_verified",
    "has_super_area",
    "super_area_unit_verified",
    "bhk",
    "bathroom",
    "bathroom_is_gt_10",
    "balcony",
    "balcony_is_gt_10",
    "parking_spaces",
    "has_parking",
    "parking_count_ambiguous",
    "floor_num",
    "total_floors",
    "location",
    "sub_area",
    "Furnishing",
    "Transaction",
    "Status",
    "facing",
    "Ownership",
]
APPROVED_22_FEATURES = APPROVED_MODEL_FEATURES

CATEGORICAL_COLS = [
    "location",
    "sub_area",
    "Furnishing",
    "Transaction",
    "Status",
    "facing",
    "Ownership",
]


class ModelLoader:
    def __init__(self):
        self._model: Optional[Any] = None
        self._metadata: Optional[Dict[str, Any]] = None
        self._allowed_categories: Dict[str, Set[str]] = {}
        self._allowed_categories_raw: Dict[str, Dict[str, str]] = {}
        self._load_lock = threading.Lock()
        self._last_error: Optional[str] = None

    def is_ready(self) -> bool:
        """
        Truthfully checks whether an approved model artifact and metadata exist,
        passed all verification checks, and are loaded in memory ready for inference.
        """
        return self._model is not None and self._metadata is not None

    @property
    def model(self) -> Optional[Any]:
        return self._model

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        return self._metadata

    @property
    def allowed_categories(self) -> Dict[str, Set[str]]:
        return self._allowed_categories

    @property
    def allowed_categories_raw(self) -> Dict[str, Dict[str, str]]:
        return self._allowed_categories_raw

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    def unload(self) -> None:
        """Safely unloads model and metadata, resetting readiness."""
        with self._load_lock:
            self._model = None
            self._metadata = None
            self._allowed_categories = {}
            self._allowed_categories_raw = {}
            self._last_error = None

    def load_artifact(
        self,
        artifact_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ) -> bool:
        """
        Loads and validates the serialized pipeline artifact and paired metadata.
        Guarantees idempotency and thread-safety via lock.
        On any verification failure, resets model state and returns False.
        """
        with self._load_lock:
            # Reset any prior state during reload attempt
            self._model = None
            self._metadata = None
            self._allowed_categories = {}
            self._allowed_categories_raw = {}
            self._last_error = None

            art_p = artifact_path or settings.resolved_artifact_path
            meta_p = metadata_path or settings.resolved_metadata_path

            if not art_p.exists():
                self._last_error = "Model artifact file does not exist."
                logger.warning("Artifact loading failed: file does not exist at configured path.")
                return False

            if not meta_p.exists():
                self._last_error = "Model metadata file does not exist."
                logger.warning("Metadata loading failed: file does not exist at configured path.")
                return False

            # 1. Parse and validate metadata JSON
            try:
                with open(meta_p, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception as e:
                self._last_error = "Model metadata is corrupt or invalid JSON."
                logger.warning("Failed to parse metadata JSON: %s", type(e).__name__)
                return False

            if not isinstance(meta, dict):
                self._last_error = "Model metadata root is not a JSON object."
                return False

            # Validate required Phase 2 metadata fields
            valid, reason = self._validate_metadata(meta)
            if not valid:
                self._last_error = f"Metadata validation failed: {reason}"
                logger.warning("Metadata verification rejected: %s", reason)
                return False

            # 2. Check runtime environment compatibility
            compat, env_reason = self._check_environment_compatibility(meta.get("environment", {}))
            if not compat:
                self._last_error = f"Environment compatibility check failed: {env_reason}"
                logger.warning("Environment check rejected: %s", env_reason)
                return False

            # 3. Verify pipeline dependencies and load model artifact via joblib
            try:
                import real_estate_ml_training.features  # noqa: F401
            except ImportError as e:
                self._last_error = f"Cannot import required pipeline dependencies: {type(e).__name__}"
                logger.error("Artifact loading aborted: cannot import real_estate_ml_training.features: %s", e)
                return False

            try:
                loaded_pipeline = joblib.load(art_p)
            except Exception as e:
                self._last_error = f"Deserialization failed: {type(e).__name__}"
                logger.warning("Model deserialization failed: %s", type(e).__name__)
                return False

            # 4. Verify pipeline structure and extract learned categories
            struct_valid, struct_reason = self._verify_and_extract_pipeline(loaded_pipeline)
            if not struct_valid:
                self._last_error = f"Pipeline structure check failed: {struct_reason}"
                logger.warning("Pipeline structure verification rejected: %s", struct_reason)
                return False

            # Model and metadata successfully verified
            self._model = loaded_pipeline
            self._metadata = meta
            logger.info(
                "Model successfully loaded and verified: model_id=%s",
                meta.get("model_id"),
            )
            return True

    def _validate_metadata(self, meta: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that metadata conforms strictly to Phase 2 specifications."""
        model_id = meta.get("model_id")
        if not model_id or not isinstance(model_id, str) or not model_id.strip():
            return False, "Missing or empty model_id"

        winning_candidate = meta.get("winning_candidate")
        if not winning_candidate or not isinstance(winning_candidate, str) or not winning_candidate.strip():
            return False, "Missing or empty winning_candidate"

        target_info = meta.get("target")
        if not isinstance(target_info, dict):
            return False, "Missing or non-object target section"
        if target_info.get("unit") != "INR":
            return False, f"Target unit must be 'INR', found: {target_info.get('unit')}"

        features_info = meta.get("features")
        if not isinstance(features_info, dict):
            return False, "Missing or non-object features section"
        all_features = features_info.get("all_features")
        if not isinstance(all_features, list):
            return False, "features.all_features must be a list"
        if all_features != APPROVED_22_FEATURES:
            return False, "features.all_features does not match approved 22-feature schema order"

        return True, ""

    def _check_environment_compatibility(self, env: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that installed libraries are compatible with recorded metadata."""
        import sklearn
        import pandas
        import numpy

        # Major version compatibility checks
        sk_rec = str(env.get("scikit_learn_version", ""))
        pd_rec = str(env.get("pandas_version", ""))
        np_rec = str(env.get("numpy_version", ""))

        if sk_rec:
            rec_major = sk_rec.split(".")[0]
            cur_major = sklearn.__version__.split(".")[0]
            if rec_major != cur_major:
                return False, f"scikit-learn major version mismatch: recorded {sk_rec}, installed {sklearn.__version__}"

        if pd_rec:
            rec_major = pd_rec.split(".")[0]
            cur_major = pandas.__version__.split(".")[0]
            if rec_major != cur_major:
                return False, f"pandas major version mismatch: recorded {pd_rec}, installed {pandas.__version__}"

        if np_rec:
            rec_major = np_rec.split(".")[0]
            cur_major = numpy.__version__.split(".")[0]
            if rec_major != cur_major:
                return False, f"numpy major version mismatch: recorded {np_rec}, installed {numpy.__version__}"

        return True, ""

    def _verify_and_extract_pipeline(self, pipeline: Any) -> Tuple[bool, str]:
        """Validates pipeline has predict method and extracts fitted categorical categories."""
        if not hasattr(pipeline, "predict") or not callable(getattr(pipeline, "predict")):
            return False, "Loaded object does not expose a callable predict method"

        # Locate the underlying Pipeline if wrapped in TransformedTargetRegressor
        inner_pipeline = getattr(pipeline, "regressor_", pipeline)

        # Attempt to inspect OneHotEncoder inside preprocessor
        try:
            preprocessor = None
            if hasattr(inner_pipeline, "named_steps"):
                preprocessor = inner_pipeline.named_steps.get("pre")
                if preprocessor is None:
                    preprocessor = inner_pipeline.named_steps.get("preprocessor")
            elif hasattr(inner_pipeline, "steps"):
                for step_name, step_obj in inner_pipeline.steps:
                    if hasattr(step_obj, "named_transformers_"):
                        preprocessor = step_obj
                        break

            if preprocessor and hasattr(preprocessor, "named_transformers_"):
                cat_sub = preprocessor.named_transformers_.get("cat")
                if cat_sub and hasattr(cat_sub, "named_steps"):
                    encoder = cat_sub.named_steps.get("encoder")
                    if encoder and hasattr(encoder, "categories_"):
                        # Extract categories for CATEGORICAL_COLS
                        allowed: Dict[str, Set[str]] = {}
                        raw_map: Dict[str, Dict[str, str]] = {}
                        for col_name, cat_arr in zip(CATEGORICAL_COLS, encoder.categories_):
                            allowed[col_name] = set()
                            raw_map[col_name] = {}
                            for c in cat_arr:
                                c_str = str(c).strip()
                                norm_key = " ".join(c_str.lower().replace("_", " ").replace("-", " ").split())
                                allowed[col_name].add(norm_key)
                                raw_map[col_name][norm_key] = c_str
                        self._allowed_categories = allowed
                        self._allowed_categories_raw = raw_map
        except Exception as e:
            logger.warning("Could not extract learned categories from pipeline: %s", e)

        return True, ""

    def get_public_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Returns a sanitized, allow-listed metadata summary suitable for public API exposure.
        Strictly excludes internal local filesystem paths, dataset dumps, or secrets.
        """
        if not self.is_ready() or self._metadata is None:
            return None

        meta = self._metadata
        target_info = meta.get("target", {})
        eval_info = meta.get("test_evaluation", {})
        winning_model = eval_info.get("winning_model", {})

        mae = winning_model.get("holdout_mae_inr")
        if mae is None:
            mae = winning_model.get("mae")
        rmse = winning_model.get("holdout_rmse_inr")
        if rmse is None:
            rmse = winning_model.get("rmse")
        r2 = winning_model.get("holdout_r2")
        if r2 is None:
            r2 = winning_model.get("r2")
        rel = winning_model.get("relative_mae_improvement_pct")
        if rel is None:
            rel = eval_info.get("relative_mae_improvement_pct")

        return {
            "model_id": meta.get("model_id"),
            "winning_candidate": meta.get("winning_candidate"),
            "target": {
                "name": target_info.get("name", "Amount(in rupees)"),
                "unit": target_info.get("unit", "INR"),
                "description": target_info.get("description", "Continuous property listing price in INR"),
            },
            "features": {
                "total_features": len(APPROVED_22_FEATURES),
                "numeric_features": APPROVED_22_FEATURES[:16],
                "categorical_features": APPROVED_22_FEATURES[16:],
            },
            "test_evaluation": {
                "winning_algorithm": winning_model.get("algorithm", meta.get("winning_candidate", "HistGradientBoostingRegressor (Tuned, log-target transform)")),
                "holdout_mae_inr": round(mae, 2) if mae is not None else None,
                "holdout_rmse_inr": round(rmse, 2) if rmse is not None else None,
                "holdout_r2": round(r2, 4) if r2 is not None else None,
                "relative_mae_improvement_pct": round(rel, 2) if rel is not None else None,
            },
            "limitations": meta.get("limitations", {}),
        }


model_loader = ModelLoader()
