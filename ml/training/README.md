# Offline ML Training Workflow

## Overview
This package contains the offline machine-learning pipeline for the Real Estate Price Prediction Platform: data auditing, cleaning, feature engineering, baseline comparison, model training, evaluation, and artifact promotion.

> **CRITICAL DATA GOVERNANCE RULE:**
> The supplied Indian property dataset (`house_prices.csv`) is not automatically approved for redistribution.
> The original dataset source, version, licence, and redistribution terms MUST be formally verified and approved by the product owner in Phase 1 before committing raw data or sharing model artifacts publicly.
> Do NOT copy raw listing data into public version control.

## Workflow Structure
- `data/`: Segregated local directories for `raw/`, `interim/`, `processed/`, and `external/` data (gitignored).
- `scripts/validate_data.py`: Recomputes dataset shape, null counts, duplicates, and target values.
- `scripts/train.py`: Trains candidate regression models against DummyRegressor baseline.
- `scripts/evaluate.py`: Generates holdout test-set metrics (MAE, RMSE, R²).
- `scripts/promote_model.py`: Validates metadata and exports approved pipeline artifact to `inference-service/artifacts/`.
