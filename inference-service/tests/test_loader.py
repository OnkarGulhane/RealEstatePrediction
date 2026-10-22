import json
import pytest
from pathlib import Path
from app.model.loader import ModelLoader, APPROVED_22_FEATURES


class DummyPredictor:
    def predict(self, X):
        return [5000000.0]


def valid_metadata_dict():
    return {
        "model_id": "test_candidate_v1",
        "winning_candidate": "HistGradientBoostingRegressor",
        "target": {
            "name": "Amount(in rupees)",
            "unit": "INR",
            "description": "Continuous price",
        },
        "features": {
            "all_features": list(APPROVED_22_FEATURES),
        },
        "environment": {
            "scikit_learn_version": "1.9.1",
            "pandas_version": "2.2.3",
            "numpy_version": "2.4.3",
            "joblib_version": "1.6.0",
        },
        "test_evaluation": {
            "winning_model": {
                "algorithm": "HistGradientBoostingRegressor",
                "holdout_mae_inr": 2693927.27,
                "holdout_rmse_inr": 8517820.69,
                "holdout_r2": 0.7104,
                "relative_mae_improvement_pct": 56.91,
            }
        },
        "limitations": {
            "historical_exposure": "documented",
        },
    }


def test_loader_missing_artifact(tmp_path):
    loader = ModelLoader()
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps(valid_metadata_dict()))
    missing_art = tmp_path / "missing.joblib"

    res = loader.load_artifact(missing_art, meta_file)
    assert res is False
    assert loader.is_ready() is False
    assert "artifact file does not exist" in loader.last_error.lower()


def test_loader_missing_metadata(tmp_path):
    loader = ModelLoader()
    art_file = tmp_path / "model.joblib"
    art_file.write_text("dummy")
    missing_meta = tmp_path / "missing.json"

    res = loader.load_artifact(art_file, missing_meta)
    assert res is False
    assert loader.is_ready() is False
    assert "metadata file does not exist" in loader.last_error.lower()


def test_loader_corrupt_json_metadata(tmp_path):
    loader = ModelLoader()
    art_file = tmp_path / "model.joblib"
    art_file.write_text("dummy")
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text("{corrupt: json::")

    res = loader.load_artifact(art_file, meta_file)
    assert res is False
    assert loader.is_ready() is False
    assert "corrupt or invalid json" in loader.last_error.lower()


def test_loader_wrong_target_unit(tmp_path):
    loader = ModelLoader()
    art_file = tmp_path / "model.joblib"
    art_file.write_text("dummy")

    bad_meta = valid_metadata_dict()
    bad_meta["target"]["unit"] = "USD"
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps(bad_meta))

    res = loader.load_artifact(art_file, meta_file)
    assert res is False
    assert "Target unit must be 'INR'" in loader.last_error


def test_loader_feature_schema_mismatch(tmp_path):
    loader = ModelLoader()
    art_file = tmp_path / "model.joblib"
    art_file.write_text("dummy")

    bad_meta = valid_metadata_dict()
    bad_meta["features"]["all_features"] = APPROVED_22_FEATURES[:-1]  # Only 21 features
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps(bad_meta))

    res = loader.load_artifact(art_file, meta_file)
    assert res is False
    assert "does not match approved 22-feature schema order" in loader.last_error


def test_loader_incompatible_dependency_version(tmp_path):
    loader = ModelLoader()
    art_file = tmp_path / "model.joblib"
    art_file.write_text("dummy")

    bad_meta = valid_metadata_dict()
    bad_meta["environment"]["scikit_learn_version"] = "99.0.0"
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps(bad_meta))

    res = loader.load_artifact(art_file, meta_file)
    assert res is False
    assert "scikit-learn major version mismatch" in loader.last_error


def test_loader_corrupt_model_deserialization(tmp_path):
    loader = ModelLoader()
    art_file = tmp_path / "model.joblib"
    art_file.write_text("not a valid pickle or joblib file")
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps(valid_metadata_dict()))

    res = loader.load_artifact(art_file, meta_file)
    assert res is False
    assert "Deserialization failed" in loader.last_error


def test_loader_model_missing_predict(tmp_path, monkeypatch):
    import joblib
    loader = ModelLoader()
    art_file = tmp_path / "model.joblib"
    joblib.dump({"not_a_model": 123}, art_file)
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps(valid_metadata_dict()))

    res = loader.load_artifact(art_file, meta_file)
    assert res is False
    assert "predict" in loader.last_error.lower()


def test_loader_get_public_metadata_allow_list(tmp_path):
    import joblib
    loader = ModelLoader()
    art_file = tmp_path / "model.joblib"
    joblib.dump(DummyPredictor(), art_file)
    meta = valid_metadata_dict()
    meta["secret_token"] = "sensitive_password_123"
    meta["raw_csv_path"] = "/secret/path/house_prices.csv"
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps(meta))

    res = loader.load_artifact(art_file, meta_file)
    assert res is True
    assert loader.is_ready() is True

    pub = loader.get_public_metadata()
    assert pub is not None
    assert pub["model_id"] == "test_candidate_v1"
    assert pub["target"]["unit"] == "INR"
    assert pub["features"]["total_features"] == 22
    assert pub["test_evaluation"]["holdout_mae_inr"] == 2693927.27
    # Verify no secret or internal path leakage
    assert "secret_token" not in pub
    assert "raw_csv_path" not in pub
    assert "sensitive_password_123" not in str(pub)
    assert "/secret/path" not in str(pub)


def test_loader_default_configured_paths(monkeypatch, tmp_path):
    from app.config import settings
    loader = ModelLoader()

    # When default configured path points to missing files
    monkeypatch.setattr(settings, "MODEL_ARTIFACT_PATH", str(tmp_path / "nonexistent.joblib"))
    monkeypatch.setattr(settings, "MODEL_METADATA_PATH", str(tmp_path / "nonexistent.json"))

    res = loader.load_artifact()
    assert res is False
    assert loader.is_ready() is False
    assert "does not exist" in loader.last_error.lower()
