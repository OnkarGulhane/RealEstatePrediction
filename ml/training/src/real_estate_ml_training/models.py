"""
Candidate regression models and evaluation utilities for real estate price prediction.
Phase 2: Offline ML training, fair comparison against Dummy baseline, and metrics computation.

Candidate models:
1. DummyRegressor (median baseline for skewed target)
2. Ridge Regressor (with log-target transform)
3. DecisionTreeRegressor (with log-target transform)
4. RandomForestRegressor (with log-target transform)
5. HistGradientBoostingRegressor (with log-target transform)
"""
from __future__ import annotations

import json
import os
from typing import Any
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.compose import TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

from real_estate_ml_training.features import (
    PropertyFeatureExtractor,
    build_preprocessor,
)


def get_candidate_models(random_state: int = 42) -> dict[str, BaseEstimator]:
    """
    Returns the agreed suite of candidate models wrapped with preprocessing pipelines.
    Models use TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1)
    to handle the heavily right-skewed INR target distribution naturally.
    """
    fe = PropertyFeatureExtractor()
    pre_scaled = build_preprocessor(scale_numeric=True)
    pre_unscaled = build_preprocessor(scale_numeric=False)

    candidates: dict[str, BaseEstimator] = {}

    # 1. Baseline: DummyRegressor (predicts median target price)
    candidates["dummy_median"] = Pipeline([
        ("feat", fe),
        ("reg", DummyRegressor(strategy="median")),
    ])

    # 2. Linear Baseline: Ridge (L2 regularized) with log-target transform
    pipe_ridge = Pipeline([
        ("feat", fe),
        ("pre", pre_scaled),
        ("reg", Ridge(alpha=10.0, random_state=random_state)),
    ])
    candidates["ridge_log"] = TransformedTargetRegressor(
        regressor=pipe_ridge,
        func=np.log1p,
        inverse_func=np.expm1,
    )

    # 3. DecisionTreeRegressor with log-target transform
    pipe_dt = Pipeline([
        ("feat", fe),
        ("pre", pre_unscaled),
        ("reg", DecisionTreeRegressor(
            max_depth=12,
            min_samples_leaf=20,
            random_state=random_state,
        )),
    ])
    candidates["decision_tree_log"] = TransformedTargetRegressor(
        regressor=pipe_dt,
        func=np.log1p,
        inverse_func=np.expm1,
    )

    # 4. RandomForestRegressor with log-target transform
    pipe_rf = Pipeline([
        ("feat", fe),
        ("pre", pre_unscaled),
        ("reg", RandomForestRegressor(
            n_estimators=100,
            max_depth=16,
            min_samples_leaf=10,
            n_jobs=-1,
            random_state=random_state,
        )),
    ])
    candidates["random_forest_log"] = TransformedTargetRegressor(
        regressor=pipe_rf,
        func=np.log1p,
        inverse_func=np.expm1,
    )

    # 5. HistGradientBoostingRegressor with log-target transform
    pipe_hgb = Pipeline([
        ("feat", fe),
        ("pre", pre_unscaled),
        ("reg", HistGradientBoostingRegressor(
            max_iter=150,
            max_leaf_nodes=45,
            min_samples_leaf=20,
            random_state=random_state,
        )),
    ])
    candidates["hist_gradient_boosting_log"] = TransformedTargetRegressor(
        regressor=pipe_hgb,
        func=np.log1p,
        inverse_func=np.expm1,
    )

    return candidates


def run_validation_hyperparameter_tuning(
    train_df: pd.DataFrame,
    y_train: np.ndarray,
    val_df: pd.DataFrame,
    y_val: np.ndarray,
    random_state: int = 42,
) -> tuple[dict[str, Any], list[dict[str, Any]], BaseEstimator]:
    """
    Executes a bounded, reproducible hyperparameter search on the validation partition.
    Only train_df and val_df are used; the holdout test set is never accessed.
    """
    search_space = [
        {"max_iter": 100, "max_leaf_nodes": 31, "learning_rate": 0.1, "min_samples_leaf": 20},
        {"max_iter": 150, "max_leaf_nodes": 31, "learning_rate": 0.1, "min_samples_leaf": 20},
        {"max_iter": 150, "max_leaf_nodes": 45, "learning_rate": 0.1, "min_samples_leaf": 20},
        {"max_iter": 150, "max_leaf_nodes": 45, "learning_rate": 0.08, "min_samples_leaf": 20},
        {"max_iter": 200, "max_leaf_nodes": 45, "learning_rate": 0.1, "min_samples_leaf": 20},
        {"max_iter": 150, "max_leaf_nodes": 63, "learning_rate": 0.1, "min_samples_leaf": 15},
    ]

    fe = PropertyFeatureExtractor()
    pre_unscaled = build_preprocessor(scale_numeric=False)

    best_mae = float("inf")
    best_params: dict[str, Any] = search_space[0]
    best_estimator: BaseEstimator | None = None
    trials: list[dict[str, Any]] = []

    for idx, params in enumerate(search_space, 1):
        pipe = Pipeline([
            ("feat", fe),
            ("pre", pre_unscaled),
            ("reg", HistGradientBoostingRegressor(**params, random_state=random_state)),
        ])
        ttr = TransformedTargetRegressor(
            regressor=pipe,
            func=np.log1p,
            inverse_func=np.expm1,
        )
        ttr.fit(train_df, y_train)
        preds = ttr.predict(val_df)
        val_metrics = compute_metrics(y_val, preds)

        trial_record = {
            "trial_index": idx,
            "params": params,
            "val_mae": val_metrics["mae"],
            "val_mae_lakh": val_metrics["mae_lakh"],
            "val_r2": val_metrics["r2"],
        }
        trials.append(trial_record)

        if val_metrics["mae"] < best_mae:
            best_mae = val_metrics["mae"]
            best_params = params
            best_estimator = ttr

    assert best_estimator is not None
    return best_params, trials, best_estimator



def compute_metrics(y_true: Any, y_pred: Any) -> dict[str, Any]:
    """
    Computes regression metrics in INR currency units.
    Checks for finite output and counts negative predictions rather than silently clipping.
    """
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)

    is_finite = np.isfinite(y_pred_arr)
    non_finite_count = int(np.sum(~is_finite))

    if non_finite_count > 0:
        return {
            "mae": float("nan"),
            "rmse": float("nan"),
            "r2": float("nan"),
            "negative_predictions": int(np.sum(y_pred_arr[is_finite] < 0)),
            "non_finite_predictions": non_finite_count,
            "median_abs_error": float("nan"),
        }

    mae = float(mean_absolute_error(y_true_arr, y_pred_arr))
    rmse = float(root_mean_squared_error(y_true_arr, y_pred_arr))
    r2 = float(r2_score(y_true_arr, y_pred_arr))
    neg_count = int(np.sum(y_pred_arr < 0))
    med_error = float(np.median(np.abs(y_true_arr - y_pred_arr)))

    return {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "negative_predictions": neg_count,
        "non_finite_predictions": 0,
        "median_abs_error": med_error,
        "mae_lakh": round(mae / 100_000.0, 2),
        "rmse_lakh": round(rmse / 100_000.0, 2),
    }


def validate_candidate_artifact(
    artifact_path: str,
    metadata_path: str,
) -> dict[str, str]:
    """Validates candidate model artifact and metadata structure."""
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Model artifact not found at '{artifact_path}'")
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found at '{metadata_path}'")

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Check required metadata fields
    required_fields = [
        "model_id",
        "winning_candidate",
        "target",
        "features",
        "dataset",
        "split",
        "test_evaluation",
        "environment",
        "training_timestamp",
        "limitations",
    ]
    for field in required_fields:
        if field not in meta:
            raise ValueError(f"Missing required metadata field: '{field}'")

    # Load model artifact
    model = joblib.load(artifact_path)

    # Smoke test on standard sample property
    sample_property = pd.DataFrame([{
        "location": "pune",
        "Title": "2 BHK Flat in Kothrud",
        "Carpet Area": "850 sqft",
        "Super Area": None,
        "Bathroom": "2",
        "Balcony": "1",
        "Car Parking": "1 Covered",
        "Floor": "3 out of 7",
        "Furnishing": "Semi-Furnished",
        "Transaction": "Resale",
        "Status": "Ready to Move",
        "facing": "East",
        "Ownership": "Freehold",
    }])

    pred = model.predict(sample_property)
    if not np.all(np.isfinite(pred)):
        raise ValueError("Model prediction returned non-finite value!")
    if pred[0] <= 0:
        raise ValueError(f"Model prediction returned non-positive value: {pred[0]}")

    pred_inr = float(pred[0])
    pred_lakh = pred_inr / 100_000.0

    return {
        "status": "PASS",
        "model_id": meta["model_id"],
        "winning_candidate": meta["winning_candidate"],
        "test_mae_lakh": f"{meta['test_evaluation']['winning_model']['mae_lakh']} L",
        "test_r2": f"{meta['test_evaluation']['winning_model']['r2']:.4f}",
        "sample_prediction_inr": f"INR {pred_inr:,.2f} ({pred_lakh:.2f} Lakh)",
    }
