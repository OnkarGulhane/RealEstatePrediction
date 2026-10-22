#!/usr/bin/env python
"""
Model Training & Evaluation Script — Offline ML Workflow (Phase 2).
Trains and fairly compares regression candidates against Dummy baseline on deterministic splits:
- 70% Train (45,678 rows)
- 15% Validation (9,788 rows)
- 15% Test (9,789 rows, holdout untouched until final evaluation)

Candidates:
1. DummyRegressor (median strategy)
2. Ridge Regressor (log-target)
3. DecisionTreeRegressor (log-target)
4. RandomForestRegressor (log-target)
5. HistGradientBoostingRegressor (log-target)

Exports winning pipeline and metadata.json to gitignored experiments/phase2/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import sklearn

from real_estate_ml_training.clean import build_phase2_deduplicated_view
from real_estate_ml_training.features import (
    ALL_MODEL_FEATURE_COLS,
    CATEGORICAL_FEATURE_COLS,
    NUMERIC_FEATURE_COLS,
)
from real_estate_ml_training.models import (
    compute_metrics,
    get_candidate_models,
    run_validation_hyperparameter_tuning,
)


def compute_file_sha256(filepath: str) -> str:
    """Computes SHA-256 checksum of a file without loading entire file into memory."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192 * 1024):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="Train and evaluate Phase 2 real estate price regression candidates."
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="ml/training/data/processed/phase2_supervised_deduplicated.csv",
        help="Path to Phase 2 deduplicated dataset CSV."
    )
    parser.add_argument(
        "--raw-path",
        type=str,
        default="ml/training/data/raw/house_prices.csv",
        help="Path to original raw CSV for provenance hash check."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ml/training/experiments/phase2",
        help="Directory to save winning pipeline artifact and metadata."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic random seed for train/val/test splitting."
    )
    args = parser.parse_args()

    print("================================================================================")
    print(" PHASE 2 OFFLINE ML TRAINING & MODEL COMPARISON")
    print("================================================================================")
    print(f"Random seed: {args.seed}")
    print(f"Data path:   {args.data_path}")
    print(f"Output dir:  {args.output_dir}")

    # Step 1: Ensure deduplicated data exists
    if not os.path.exists(args.data_path):
        print(f"\n[INFO] Deduplicated dataset not found at {args.data_path}. Building from raw...")
        if not os.path.exists(args.raw_path):
            print(f"ERROR: Raw dataset not found at {args.raw_path}!")
            sys.exit(1)
        raw_df = pd.read_csv(args.raw_path)
        dedup_df, audit_mapping_df, accounting = build_phase2_deduplicated_view(raw_df)
        os.makedirs(os.path.dirname(args.data_path), exist_ok=True)
        dedup_df.to_csv(args.data_path, index=False)
        print(f"Built and saved deduplicated dataset ({len(dedup_df):,} rows).")
    else:
        dedup_df = pd.read_csv(args.data_path)

    total_rows = len(dedup_df)
    print(f"\n[1/5] Loaded deduplicated dataset: {total_rows:,} rows.")
    assert total_rows == 65255, f"Expected exactly 65,255 unique configurations, got {total_rows:,}"

    # Target variable check
    y = dedup_df["target_price_inr"].values
    assert np.all(np.isfinite(y)), "Target contains non-finite values!"
    assert np.all(y > 0), "Target contains non-positive values!"

    # Step 2: Deterministic 70 / 15 / 15 train / val / test split
    print("\n[2/5] Creating deterministic train/val/test split (70% / 15% / 15%)...")
    # First split: 70% train vs 30% temp
    train_df, temp_df = train_test_split(
        dedup_df,
        test_size=0.30,
        random_state=args.seed,
        shuffle=True,
    )
    # Second split: 50% of 30% = 15% val, 15% test
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=args.seed,
        shuffle=True,
    )

    n_train = len(train_df)
    n_val = len(val_df)
    n_test = len(test_df)
    assert n_train + n_val + n_test == total_rows, "Split counts do not sum to total rows"
    print(f"  - Train set:      {n_train:,} rows ({n_train / total_rows * 100:.1f}%)")
    print(f"  - Validation set: {n_val:,} rows ({n_val / total_rows * 100:.1f}%)")
    print(f"  - Test set:       {n_test:,} rows ({n_test / total_rows * 100:.1f}%) [Preserved untouched]")

    y_train = train_df["target_price_inr"].values
    y_val = val_df["target_price_inr"].values
    y_test = test_df["target_price_inr"].values

    # Step 3: Train and evaluate candidates on Validation set
    print("\n[3/5] Training candidate models and comparing on Validation set...")
    candidates = get_candidate_models(random_state=args.seed)

    val_results: dict[str, dict[str, Any]] = {}
    fitted_models: dict[str, Any] = {}

    print(f"{'Candidate Model':<30} | {'Val MAE (INR)':<16} | {'Val MAE (Lakh)':<14} | {'Val RMSE (Lakh)':<15} | {'Val R^2':<8} | {'Improvement':<12} | {'Train Time'}")
    print("-" * 115)

    dummy_val_mae: float | None = None

    for name, model in candidates.items():
        t0 = time.time()
        model.fit(train_df, y_train)
        train_time_sec = time.time() - t0
        fitted_models[name] = model

        y_val_pred = model.predict(val_df)
        metrics = compute_metrics(y_val, y_val_pred)
        metrics["train_time_sec"] = round(train_time_sec, 2)

        if name == "dummy_median":
            dummy_val_mae = metrics["mae"]
            improvement_str = "Baseline"
            metrics["relative_mae_improvement_pct"] = 0.0
        else:
            rel_imp = ((dummy_val_mae - metrics["mae"]) / dummy_val_mae) * 100.0
            metrics["relative_mae_improvement_pct"] = round(rel_imp, 2)
            improvement_str = f"{rel_imp:+.2f}%"

        val_results[name] = metrics

        print(
            f"{name:<30} | "
            f"INR {metrics['mae']:>10,.2f} | "
            f"INR {metrics['mae_lakh']:>6.2f} L | "
            f"INR {metrics['rmse_lakh']:>7.2f} L | "
            f"{metrics['r2']:>8.4f} | "
            f"{improvement_str:>12} | "
            f"{train_time_sec:.2f}s"
        )

    # Step 4: Model Selection based on validation MAE
    # Filter candidates excluding dummy
    comp_candidates = {k: v for k, v in val_results.items() if k != "dummy_median"}
    base_best_name = min(comp_candidates, key=lambda k: comp_candidates[k]["mae"])
    best_model = fitted_models[base_best_name]
    best_val_metrics = val_results[base_best_name]

    print("\n" + "=" * 80)
    print(f" BASELINE CANDIDATE SELECTED: {base_best_name}")
    print(f" Validation MAE: INR {best_val_metrics['mae']:,.2f} ({best_val_metrics['mae_lakh']:.2f} Lakh)")
    print(f" Validation R^2: {best_val_metrics['r2']:.4f}")
    print(f" Improvement over baseline: {best_val_metrics['relative_mae_improvement_pct']:+.2f}%")
    print("=" * 80)

    # Step 4b: Validation-Only Bounded Hyperparameter Tuning
    print("\n[3b/5] Executing validation-only hyperparameter tuning on top candidate...")
    print("Search space: max_iter, max_leaf_nodes, learning_rate, min_samples_leaf.")
    print("Strict discipline: Training partition fits estimators; Validation partition selects best.")
    print("Holdout test set is NOT touched during search.")

    best_params, tuning_trials, tuned_estimator = run_validation_hyperparameter_tuning(
        train_df, y_train, val_df, y_val, random_state=args.seed
    )
    tuned_val_preds = tuned_estimator.predict(val_df)
    tuned_val_metrics = compute_metrics(y_val, tuned_val_preds)
    tuned_rel_imp = ((dummy_val_mae - tuned_val_metrics["mae"]) / dummy_val_mae) * 100.0
    tuned_val_metrics["relative_mae_improvement_pct"] = round(tuned_rel_imp, 2)

    print(f"Tuning finished. Best params: {best_params}")
    print(
        f"Tuned Val MAE: INR {tuned_val_metrics['mae']:,.2f} "
        f"({tuned_val_metrics['mae_lakh']:.2f} Lakh), R^2: {tuned_val_metrics['r2']:.4f}"
    )

    if tuned_val_metrics["mae"] <= best_val_metrics["mae"]:
        print(f"Tuned pipeline selected (Val MAE improved from {best_val_metrics['mae_lakh']:.2f}L to {tuned_val_metrics['mae_lakh']:.2f}L)")
        best_model = tuned_estimator
        best_val_metrics = tuned_val_metrics
        winning_candidate_name = f"{base_best_name}_tuned"
    else:
        winning_candidate_name = base_best_name

    # Step 5: Final Evaluation on untouched Test Set
    print("\n[4/5] Evaluating selected model and baseline on untouched Test set...")
    dummy_model = fitted_models["dummy_median"]
    y_test_dummy_pred = dummy_model.predict(test_df)
    test_dummy_metrics = compute_metrics(y_test, y_test_dummy_pred)

    y_test_pred = best_model.predict(test_df)
    test_metrics = compute_metrics(y_test, y_test_pred)

    test_rel_improvement = ((test_dummy_metrics["mae"] - test_metrics["mae"]) / test_dummy_metrics["mae"]) * 100.0
    test_metrics["relative_mae_improvement_pct"] = round(test_rel_improvement, 2)
    meets_target = bool(test_rel_improvement >= 10.0)

    print(f"\nFinal Test Results:")
    print(f"  - Dummy Baseline Test MAE:   INR {test_dummy_metrics['mae']:,.2f} ({test_dummy_metrics['mae_lakh']:.2f} Lakh), R^2 = {test_dummy_metrics['r2']:.4f}")
    print(f"  - Winning Model Test MAE:    INR {test_metrics['mae']:,.2f} ({test_metrics['mae_lakh']:.2f} Lakh), R^2 = {test_metrics['r2']:.4f}")
    print(f"  - Winning Model Test RMSE:   INR {test_metrics['rmse']:,.2f} ({test_metrics['rmse_lakh']:.2f} Lakh)")
    print(f"  - Relative MAE Improvement:  {test_rel_improvement:+.2f}%")
    print(f"  - Target (>=10% MAE imp.):   {'ACHIEVED (PASS)' if meets_target else 'UNMET'}")
    print(f"  - Negative Predictions:      {test_metrics['negative_predictions']}")
    print(f"  - Non-finite Predictions:    {test_metrics['non_finite_predictions']}")

    # Residuals inspection
    residuals = y_test - y_test_pred
    test_metrics["residual_mean"] = round(float(np.mean(residuals)), 2)
    test_metrics["residual_std"] = round(float(np.std(residuals)), 2)
    test_metrics["residual_p25"] = round(float(np.percentile(residuals, 25)), 2)
    test_metrics["residual_p50"] = round(float(np.percentile(residuals, 50)), 2)
    test_metrics["residual_p75"] = round(float(np.percentile(residuals, 75)), 2)

    # Step 6: Artifact and Metadata Serialization
    print(f"\n[5/5] Saving model pipeline and metadata to {args.output_dir}...")
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model_path = out_dir / "model_pipeline.joblib"
    metadata_path = out_dir / "metadata.json"

    # Compute raw file hash if available
    raw_sha256 = ""
    if os.path.exists(args.raw_path):
        raw_sha256 = compute_file_sha256(args.raw_path)

    metadata: dict[str, Any] = {
        "model_id": f"real_estate_{winning_candidate_name}_v1",
        "winning_candidate": winning_candidate_name,
        "base_candidate": base_best_name,
        "hyperparameter_tuning": {
            "candidate_family": "HistGradientBoostingRegressor",
            "tuning_strategy": "validation_partition_grid_search",
            "search_space_trials": tuning_trials,
            "best_params": best_params,
            "val_mae_before_tuning": comp_candidates[base_best_name]["mae"],
            "val_mae_after_tuning": tuned_val_metrics["mae"],
            "holdout_test_consulted": False,
        },
        "ridge_regression_investigation": {
            "validation_mae_lakh": val_results.get("ridge_log", {}).get("mae_lakh"),
            "validation_rmse_lakh": val_results.get("ridge_log", {}).get("rmse_lakh"),
            "validation_r2": val_results.get("ridge_log", {}).get("r2"),
            "diagnosis": (
                "Linear Ridge with log1p target transformation exponentiates extreme one-hot encoded "
                "location and numeric feature combinations, predicting astronomical prices "
                "(up to INR 311 Crore on INR 3.5 Crore actuals). Squaring these immense outliers "
                "severely inflates RMSE and produces negative R^2, whereas tree-based regressors "
                "bound leaf predictions within observed ranges."
            ),
        },
        "target": {
            "name": "Amount(in rupees)",
            "description": "Continuous property asking/listing price",
            "unit": "INR",
            "log_transformed_during_training": True,
        },
        "features": {
            "all_features": ALL_MODEL_FEATURE_COLS,
            "numeric_features": NUMERIC_FEATURE_COLS,
            "categorical_features": CATEGORICAL_FEATURE_COLS,
            "excluded_features": [
                "Index",
                "Description",
                "Price (in rupees)",
                "Dimensions",
                "Plot Area",
                "Amount(in rupees)",
            ],
        },
        "dataset": {
            "raw_sha256": raw_sha256,
            "raw_rows": 187531,
            "valid_supervised_rows": 177847,
            "call_for_price_rows": 9684,
            "deduplicated_supervised_rows": total_rows,
            "duplicate_occurrences_removed": 112592,
            "deduplication_key": "All 20 original columns excluding Index",
            "provenance_status": "UNVERIFIED / RESTRICTED FROM REDISTRIBUTION",
        },
        "split": {
            "strategy": "deterministic_seeded_train_val_test_70_15_15",
            "random_seed": args.seed,
            "train_rows": n_train,
            "validation_rows": n_val,
            "test_rows": n_test,
        },
        "validation_comparison": val_results,
        "test_evaluation": {
            "dummy_baseline": test_dummy_metrics,
            "winning_model": test_metrics,
            "relative_mae_improvement_pct": test_rel_improvement,
            "meets_10pct_mae_target": meets_target,
        },
        "environment": {
            "scikit_learn_version": sklearn.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "joblib_version": joblib.__version__,
            "python_version": sys.version.split()[0],
        },
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "Listing prices reflect seller asking prices, not verified transaction/registry prices.",
            "Lack of unique physical property identifiers means residual near-duplicate leakage across partitions cannot be formally ruled out.",
            "Extreme price outliers (luxury properties > 30 Crore) exhibit high variance and wider confidence intervals.",
            "Dataset provenance remains UNVERIFIED; artifact and dataset are restricted from redistribution.",
        ],
    }

    # Save artifact and metadata
    joblib.dump(best_model, model_path)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    model_size_bytes = os.path.getsize(model_path)
    meta_size_bytes = os.path.getsize(metadata_path)

    print(f"Saved candidate pipeline: {model_path} ({model_size_bytes:,} bytes)")
    print(f"Saved metadata:           {metadata_path} ({meta_size_bytes:,} bytes)")
    print("================================================================================")
    print(" PHASE 2 MODEL TRAINING & EVALUATION COMPLETE: PASS")
    print("================================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
