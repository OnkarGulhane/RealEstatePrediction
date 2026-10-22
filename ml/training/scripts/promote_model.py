#!/usr/bin/env python
"""
Model Promotion & Validation Script — Offline ML Workflow (Phase 2).
Validates candidate model artifact and metadata before Phase 3 inference service deployment.
Performs verification checks:
- Candidate model artifact existence and integrity.
- Metadata completeness (dataset hash, metrics, parameters, limitations).
- Prediction sanity smoke tests on sample payload.
- Ensures no fake or unverified artifact is promoted.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from real_estate_ml_training.models import validate_candidate_artifact


def main():
    parser = argparse.ArgumentParser(
        description="Validate and smoke-test evaluated model candidate before Phase 3."
    )
    parser.add_argument(
        "--artifact-path",
        type=str,
        default="ml/training/experiments/phase2/model_pipeline.joblib",
        help="Path to evaluated candidate model artifact."
    )
    parser.add_argument(
        "--metadata-path",
        type=str,
        default="ml/training/experiments/phase2/metadata.json",
        help="Path to candidate metadata JSON."
    )
    args = parser.parse_args()

    print("================================================================================")
    print(" MODEL CANDIDATE PROMOTION & VALIDATION CHECK")
    print("================================================================================")
    print(f"Artifact path: {args.artifact_path}")
    print(f"Metadata path: {args.metadata_path}")

    try:
        report = validate_candidate_artifact(args.artifact_path, args.metadata_path)
        print("\nValidation Results:")
        print(f"  - Status:              {report['status']}")
        print(f"  - Model ID:            {report['model_id']}")
        print(f"  - Algorithm:           {report['winning_candidate']}")
        print(f"  - Test MAE:            {report['test_mae_lakh']}")
        print(f"  - Test R^2:            {report['test_r2']}")
        print(f"  - Sample Prediction:   {report['sample_prediction_inr']}")
        print("\nCandidate model artifact is validated and ready for Phase 3 inference service.")
        print("================================================================================")
        print(" PROMOTION VALIDATION: PASS")
        print("================================================================================")
        return 0
    except Exception as e:
        print(f"\nVALIDATION FAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
