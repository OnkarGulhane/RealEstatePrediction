# Dataset & Machine Learning Specification (Starter Draft)

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Status | Planning Draft — Phase 0 / Phase 1 Boundary |
| Dataset under audit | `house_prices.csv` (provided in user archive) |
| Target Variable | Continuous Listing Price in Indian Rupees (`Amount(in rupees)`) |

---

## 1. Preliminary Dataset Profile

A preliminary inspection of the raw `house_prices.csv` dataset revealed:

- **Total Rows:** 187,531
- **Total Columns:** 21
- **Target `Amount(in rupees)` parsed:** ~177,847 records
- **Non-price Target rows:** 9,684 records contain `'Call for Price'` (must be excluded from supervised target training)
- **Duplicate Occurrences:** **119,339 rows** are identical across all 20 property columns when ignoring the unique row identifier `Index`, leaving only 68,192 unique row combinations.
- **Empty Columns:** `Dimensions` and `Plot Area` are 100% blank.
- **High Missingness:** `Car Parking` (103,357 missing), `Society` (109,678 missing), `Carpet Area` (80,673 missing), `Super Area` (107,685 missing), `facing` (70,233 missing).

---

## 2. Target Leakage Prevention Rules

1. **`Index`:** Strictly dropped from all training data.
2. **`Description`:** Excluded from predictive features in initial release due to potential price mentions or target leakage.
3. **`Price (in rupees)`:** Excluded by default until its derivation and leakage risk are formally investigated and resolved.

---

## 3. Offline ML Workflow Overview (`ml/training/`)

```text
Raw Data (house_prices.csv)
          │
          ▼
   1. Data Audit & Validation (scripts/validate_data.py)
          │
          ▼
   2. Clean, Normalize & Impute (scripts/train.py)
      - Parse Lac / Cr into numeric INR
      - Standardize area units to sqft
      - One-Hot / Target encoding for locations & categories
          │
          ▼
   3. Train/Val/Test Split (Preserving untouched holdout test set)
          │
          ▼
   4. Model Comparison (Dummy baseline vs Ridge vs RandomForest vs HistGradientBoosting)
          │
          ▼
   5. Evaluation & Residual Analysis (scripts/evaluate.py)
      - MAE, RMSE, R²
          │
          ▼
   6. Packaging & Promotion (scripts/promote_model.py)
      - Exports single pipeline artifact (model_pipeline.joblib)
      - Generates metadata.json
```

---

## 4. Approved Dataset Publication & Cleaning Principles

The following principles are approved by the product owner for Phase 1 data work:

1. **Redistribution & Commit Policy:** Raw or cleaned dataset files must NOT be committed to git or redistributed until original source, licence, attribution, and redistribution rights are verified.
2. **Index Feature Exclusion:** `Index` is strictly an arbitrary row index and is not a model feature.
3. **Duplicate Investigation:** Audit exact and near-duplicate listing rows rigorously; do not blindly delete all repeated rows without evidence. Establish a leakage-aware split after duplicate investigation.
4. **Deterministic Target Parsing:** Parse supported Lac/Cr values into numeric INR using deterministic, tested rules. Exclude `Call for Price` and unparseable targets from supervised training and report exact counts/reasons.
5. **Area Representation:** Do not conflate `Carpet Area` and `Super Area`. Convert only verified area units; do not guess unknown regional units.
6. **Leakage & Unclear Field Exclusion:** Exclude unclear or target-leaking fields such as `Description` and `Price (in rupees)` unless their provenance and derivation are explicitly verified.
7. **Missing & Extreme Value Handling:** Handle missing values using transformations fitted strictly on training data splits. Investigate extreme values rather than blindly deleting them.
8. **Pending Phase 1 Evidence:** The exact deduplication policy, final feature set, area conversion outcomes, and eligible row counts remain pending Phase 1 audit evidence.
