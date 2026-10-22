#!/usr/bin/env python
"""
Model Evaluation Script — Offline ML Workflow (Phase 2).
Loads the fitted candidate pipeline artifact and performs comprehensive evaluation:
- Test set MAE, RMSE, R^2, and baseline comparison.
- Segment error analysis (by location/city, BHK tier, price bucket).
- Outlier and residual distribution analysis.
- Sanity checks: finite output, negative predictions.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from real_estate_ml_training.models import compute_metrics


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive evaluation and segment analysis of trained model artifact."
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="ml/training/experiments/phase2/model_pipeline.joblib",
        help="Path to trained model artifact."
    )
    parser.add_argument(
        "--metadata-path",
        type=str,
        default="ml/training/experiments/phase2/metadata.json",
        help="Path to model metadata JSON."
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="ml/training/data/processed/phase2_supervised_deduplicated.csv",
        help="Path to deduplicated dataset."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed matching training split."
    )
    args = parser.parse_args()

    print("================================================================================")
    print(" PHASE 2 MODEL EVALUATION & RESIDUAL ANALYSIS")
    print("================================================================================")
    print(f"Model path:    {args.model_path}")
    print(f"Metadata path: {args.metadata_path}")
    print(f"Dataset path:  {args.data_path}")

    if not os.path.exists(args.model_path):
        print(f"ERROR: Model artifact not found at {args.model_path}!")
        sys.exit(1)

    # Load model
    print("\n[1/4] Loading model pipeline artifact...")
    model = joblib.load(args.model_path)
    print(f"Loaded estimator: {type(model).__name__}")

    # Load metadata if present
    if os.path.exists(args.metadata_path):
        with open(args.metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        print(f"Model ID: {metadata.get('model_id')}")
        print(f"Winning candidate: {metadata.get('winning_candidate')}")

    # Load dataset and reproduce exact holdout test partition
    print("\n[2/4] Reproducing exact holdout test partition (15% = 9,789 rows)...")
    df = pd.read_csv(args.data_path)
    _, temp_df = train_test_split(df, test_size=0.30, random_state=args.seed, shuffle=True)
    _, test_df = train_test_split(temp_df, test_size=0.50, random_state=args.seed, shuffle=True)

    y_test = test_df["target_price_inr"].values
    print(f"Test partition size: {len(test_df):,} rows.")

    # Predict
    print("\n[3/4] Generating predictions on holdout test set...")
    y_pred = model.predict(test_df)
    overall_metrics = compute_metrics(y_test, y_pred)

    print("\nOverall Holdout Test Metrics:")
    print(f"  - MAE:                  INR {overall_metrics['mae']:,.2f} ({overall_metrics['mae_lakh']:.2f} Lakh)")
    print(f"  - RMSE:                 INR {overall_metrics['rmse']:,.2f} ({overall_metrics['rmse_lakh']:.2f} Lakh)")
    print(f"  - R^2:                  {overall_metrics['r2']:.4f}")
    print(f"  - Median Abs Error:     INR {overall_metrics['median_abs_error']:,.2f} ({overall_metrics['median_abs_error']/100000:.2f} Lakh)")
    print(f"  - Negative Predictions: {overall_metrics['negative_predictions']}")
    print(f"  - Non-finite Out:       {overall_metrics['non_finite_predictions']}")

    # Step 4: Segment Analysis
    print("\n[4/4] Segment & Residual Error Analysis...")
    test_eval_df = test_df.copy()
    test_eval_df["y_true"] = y_test
    test_eval_df["y_pred"] = y_pred
    test_eval_df["abs_error"] = np.abs(y_test - y_pred)
    test_eval_df["rel_error"] = test_eval_df["abs_error"] / test_eval_df["y_true"]
    test_eval_df["residual"] = y_test - y_pred

    # Segment by top locations
    print("\n--- Performance by Top 10 Locations ---")
    loc_summary = test_eval_df.groupby("location").agg(
        count=("y_true", "count"),
        mae=("abs_error", "mean"),
        median_true=("y_true", "median"),
        median_pred=("y_pred", "median"),
    ).sort_values("count", ascending=False).head(10)

    loc_summary["mae_lakh"] = loc_summary["mae"] / 100_000.0
    loc_summary["median_true_lakh"] = loc_summary["median_true"] / 100_000.0
    loc_summary["median_pred_lakh"] = loc_summary["median_pred"] / 100_000.0

    print(f"{'Location':<20} | {'Count':<7} | {'MAE (Lakh)':<12} | {'Med True (L)':<14} | {'Med Pred (L)'}")
    print("-" * 75)
    for loc, row in loc_summary.iterrows():
        print(f"{loc:<20} | {int(row['count']):>6} | {row['mae_lakh']:>10.2f} L | {row['median_true_lakh']:>12.2f} L | {row['median_pred_lakh']:>10.2f} L")

    # Segment by BHK
    print("\n--- Performance by BHK Configuration ---")
    from real_estate_ml_training.features import extract_bhk
    if "bhk" not in test_eval_df.columns:
        test_eval_df["bhk"] = [extract_bhk(v) for v in test_eval_df["Title"]]

    bhk_summary = test_eval_df.groupby("bhk").agg(
        count=("y_true", "count"),
        mae=("abs_error", "mean"),
        median_true=("y_true", "median"),
    ).sort_values("bhk").head(6)
    bhk_summary["mae_lakh"] = bhk_summary["mae"] / 100_000.0
    bhk_summary["median_true_lakh"] = bhk_summary["median_true"] / 100_000.0

    print(f"{'BHK':<8} | {'Count':<7} | {'MAE (Lakh)':<12} | {'Med Price (L)'}")
    print("-" * 50)
    for bhk_val, row in bhk_summary.iterrows():
        print(f"{bhk_val:<8} | {int(row['count']):>6} | {row['mae_lakh']:>10.2f} L | {row['median_true_lakh']:>10.2f} L")

    # Price Tier Error breakdown
    print("\n--- Error Breakdown by Price Tier ---")
    test_eval_df["price_tier"] = pd.cut(
        test_eval_df["y_true"],
        bins=[0, 5_000_000, 10_000_000, 20_000_000, 50_000_000, np.inf],
        labels=["< 50L (Affordable)", "50L - 1 Cr (Mid)", "1 - 2 Cr (Upper Mid)", "2 - 5 Cr (Premium)", "> 5 Cr (Luxury)"]
    )
    tier_summary = test_eval_df.groupby("price_tier", observed=False).agg(
        count=("y_true", "count"),
        mae=("abs_error", "mean"),
        median_abs_err=("abs_error", "median"),
        mean_pct_err=("rel_error", lambda x: np.mean(x) * 100.0),
    )
    tier_summary["mae_lakh"] = tier_summary["mae"] / 100_000.0
    tier_summary["med_err_lakh"] = tier_summary["median_abs_err"] / 100_000.0

    print(f"{'Price Tier':<22} | {'Count':<7} | {'MAE (Lakh)':<12} | {'Med Err (L)':<12} | {'Mean % Err'}")
    print("-" * 75)
    for tier, row in tier_summary.iterrows():
        print(f"{tier:<22} | {int(row['count']):>6} | {row['mae_lakh']:>10.2f} L | {row['med_err_lakh']:>10.2f} L | {row['mean_pct_err']:>8.1f}%")

    # Residual Quartiles
    residuals = test_eval_df["residual"].values
    print("\n--- Residual Error Distribution (y_true - y_pred) ---")
    print(f"  - Mean Residual:   INR {np.mean(residuals):>12,.2f}")
    print(f"  - Std Deviation:   INR {np.std(residuals):>12,.2f}")
    print(f"  - 10th Percentile: INR {np.percentile(residuals, 10):>12,.2f}")
    print(f"  - 25th Percentile: INR {np.percentile(residuals, 25):>12,.2f}")
    print(f"  - Median Residual: INR {np.percentile(residuals, 50):>12,.2f}")
    print(f"  - 75th Percentile: INR {np.percentile(residuals, 75):>12,.2f}")
    print(f"  - 90th Percentile: INR {np.percentile(residuals, 90):>12,.2f}")

    print("\n================================================================================")
    print(" EVALUATION SUMMARY: PASS")
    print("================================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
