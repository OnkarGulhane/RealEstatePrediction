# Dataset & Machine Learning Specification (Starter Draft)

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Status | Phase 2 Offline Training & Evaluation Complete (Candidate Pipeline Versioned) |
| Dataset under audit | `house_prices.csv` (provided in user archive, 106,149,815 bytes) |
| Target Variable | Continuous Listing Price in Indian Rupees (`Amount(in rupees)`) |
| Approval Date | Phase 1 Approved (2026-10-22); Phase 2 Implementation Ready for Owner Review |
| Provenance / Licence | **UNVERIFIED / RESTRICTED FROM REDISTRIBUTION** |

---

## 1. Audited Dataset Profile

The Phase 1 deterministic audit of the raw `house_prices.csv` dataset established:

- **Total Rows & Columns:** Exactly 187,531 rows, 21 columns.
- **Target `Amount(in rupees)` Reconciled Breakdown:**
  - Valid Supervised Target: **177,847 records** (112,568 Lac/Lakh + 65,279 Cr/Crore).
  - Excluded `Call for Price`: **9,684 records**.
  - Blank / Unparseable: **0 records** (100% accounted for: `177,847 + 9,684 = 187,531`).
- **Mutually Exclusive Area Partition:**
  - `Carpet Area` only: **106,858 listings** (Verified: 100,428 sqft, 5,526 sqyrd, 894 sqm; Regional: 10).
  - `Super Area` only: **79,846 listings** (Verified: 75,406 sqft, 3,547 sqyrd, 873 sqm; Regional: 20).
  - Both areas populated: **0 listings** (Zero co-occurrence across entire dataset).
  - Neither area populated: **827 listings**.
  - Partition Sum: `106,858 + 79,846 + 0 + 827 = 187,531` (**100% exact match**).
- **Duplicate Analysis:**
  - Full-row duplicates (including `Index`): **0**.
  - All-raw duplicate listings excluding `Index`: **119,339 rows** (leaving **68,192 unique property configurations** across all target categories).
  - Valid-target subset (177,847 rows): **65,255 unique property configurations** eligible for supervised training (112,592 duplicate occurrences).
  - `Call for Price` subset (9,684 rows): **2,937 unique property configurations** (6,747 duplicate occurrences).
  - Reconciled cross-sum: `65,255 + 2,937 = 68,192` unique; `112,592 + 6,747 = 119,339` duplicates.
- **100% Blank Columns (Dropped):** `Dimensions` (187,531 nulls) and `Plot Area` (187,531 nulls).
- **Target Leakage Fields (Excluded):** `Price (in rupees)` (rate/sqft derived from target) and `Description` (quotes asking prices verbatim).

---

## 2. Target Leakage Prevention Rules

1. **`Index`:** Strictly dropped from all training data.
2. **`Description`:** Excluded from predictive features in initial release due to potential price mentions or target leakage.
3. **`Price (in rupees)`:** Excluded by default until its derivation and leakage risk are formally investigated and resolved.
4. **`Amount(in rupees)`:** Target variable; transformed via `log1p` during model fitting and inverted via `expm1` for metric calculation in INR.
5. **Preprocessing Isolation:** All imputers and OneHotEncoders are fitted strictly on the 70% training partition; no holdout validation or test statistics leak into encoders.

---

## 3. Offline ML Workflow Overview (`ml/training/`)

```text
Raw Data (house_prices.csv, 187,531 rows)
          │
          ▼
   1. Data Audit & Validation (scripts/validate_data.py)
          │
          ▼
   2. Deduplication & Audit Mapping (scripts/prepare_data.py --phase2)
      - Filter valid targets (177,847 rows)
      - Deduplicate across 20 property columns excluding Index (65,255 rows)
      - Retain auditable row mapping (phase2_audit_mapping.csv)
          │
          ▼
   3. Seeded Train/Val/Test Split (seed=42; 70% / 15% / 15%)
      - Train: 45,678 rows
      - Validation: 9,788 rows
      - Test: 9,789 rows (untouched until final evaluation)
          │
          ▼
   4. Model Comparison on Validation Set
      - Dummy Baseline (median strategy)
      - Ridge Regressor (log-target)
      - DecisionTreeRegressor (log-target)
      - RandomForestRegressor (log-target)
      - HistGradientBoostingRegressor (log-target)
          │
          ▼
   5. Selection & Final Evaluation on Untouched Test Set (scripts/evaluate.py)
      - Selected: HistGradientBoostingRegressor
      - Test MAE: INR 27.43 Lakh (+56.12% improvement over baseline)
      - Test R²: 0.7072
          │
          ▼
   6. Promotion Validation Check (scripts/promote_model.py)
      - Validates local artifact (experiments/phase2/model_pipeline.joblib)
      - Validates metadata (experiments/phase2/metadata.json)
```

---

## 4. Approved Phase 2 Dataset & Modeling Policies (Executed)

1. **Exact Duplicates Policy (EXECUTED):**
   - The primary supervised training view (`phase2_supervised_deduplicated.csv`) retains exactly **65,255 unique property configurations** (removing 112,592 duplicate occurrences).
   - Auditable mapping (`phase2_audit_mapping.csv`) preserves the link from each `config_id` to its primary index and all source indices.
   - Raw source CSV and Phase 1 interim prepared CSV were strictly preserved and not modified.
   - Grouping key investigation: 56.5% of listings lack `Society`, and `location + Title` conflates disparate buildings across entire sectors. No defensible physical property identity exists; deterministic seeded split (70/15/15) was applied after exact deduplication, and residual near-duplicate leakage is explicitly recorded as a known limitation.

2. **Area Features Strategy (EXECUTED):**
   - Kept `carpet_area_sqft` and `super_area_sqft` strictly separate.
   - Zero co-occurrence confirmed; no carpet/super ratio created.
   - Separate presence indicators (`has_carpet_area`, `has_super_area`) and verified unit flags (`carpet_area_unit_verified`, `super_area_unit_verified`) retained.

3. **Regional / Ambiguous Units Handling (EXECUTED):**
   - The 30 regional-unit records were preserved in the dataset with standardized area set to `NaN` (handled via median imputation in preprocessing).

4. **Dataset Provenance & Licensing (ENFORCED):**
   - All dataset views (`*.csv`), model artifacts (`*.joblib`), and metadata (`*.json`) remain strictly local-only and gitignored. Status remains **`UNVERIFIED / RESTRICTED FROM REDISTRIBUTION`**.

---

## 5. Final Selected Feature Schema

The final fitted pipeline consumes **22 total features** (16 numeric and 6 categorical), strictly excluding identifiers and target-leaking fields.

| Feature Name | Type | Source / Derivation | Availability at Prediction Time | Leakage & Handling Rationale |
|---|---|---|---|---|
| `carpet_area_sqft` | Numeric (float) | `Carpet Area` parsed and converted to sqft (verified units only) | Available (form input) | Direct physical dimension. Median imputed on training partition. |
| `super_area_sqft` | Numeric (float) | `Super Area` parsed and converted to sqft (verified units only) | Available (form input) | Direct physical dimension. Kept strictly separate from carpet area. |
| `has_carpet_area` | Binary (0/1) | 1 if Carpet Area was specified in listing, 0 otherwise | Available | Distinguishes absence of carpet area from zero. |
| `carpet_area_unit_verified` | Binary (0/1) | 1 if Carpet Area was converted using a verified standard unit | Available | Distinguishes unverified provided units from absent values. |
| `has_super_area` | Binary (0/1) | 1 if Super Area was specified in listing, 0 otherwise | Available | Distinguishes absence of super area from zero. |
| `super_area_unit_verified` | Binary (0/1) | 1 if Super Area was converted using a verified standard unit | Available | Distinguishes unverified provided units from absent values. |
| `bhk` | Numeric (float) | Deterministic regex extraction from `Title` (`(\d+)\s*bhk`, `studio` -> 1) | Available (form dropdown) | Core property configuration. 99.98% extraction coverage. |
| `bathroom` | Numeric (float) | `Bathroom` column cleaned (`> 10` mapped to 10.0) | Available | Essential amenity count. Median imputed. |
| `bathroom_is_gt_10` | Binary (0/1) | 1 if raw `Bathroom` was literal `> 10` (open interval), 0 otherwise | Available | Audited; flags top-coded dropdown records (27 rows). |
| `balcony` | Numeric (float) | `Balcony` column cleaned (`> 10` mapped to 10.0) | Available | Amenity count. Median imputed. |
| `balcony_is_gt_10` | Binary (0/1) | 1 if raw `Balcony` was literal `> 10` (open interval), 0 otherwise | Available | Audited; flags top-coded dropdown records (13 rows). |
| `parking_spaces` | Numeric (float) | `Car Parking` parsed under Treatment B: counts $\le 20$ preserved; numbers $> 20$ set to NaN (median imputed on training partition only); qualitative text set to 1.0; null/empty set to 0.0 | Available | Preserves legitimate multi-car counts; treats numbers $> 20$ as semantic-unknown without asserting a factual count of 1. |
| `has_parking` | Binary (0/1) | 1 if parking information was populated, 0 if null/empty | Available | Parking presence indicator. |
| `parking_count_ambiguous` | Binary (0/1) | 1 if parking text contained a flat/slot number $> 20$ (e.g. 402 Covered), 0 otherwise | Available | Flags magnitude $> 20$ ambiguity (299 deduplicated rows). |
| `floor_num` | Numeric (float) | `Floor` parsed (`X out of Y`: Ground -> 0, Basement -> -1) | Available | Vertical position. Median imputed. |
| `total_floors` | Numeric (float) | `Floor` parsed (`X out of Y`: total building floors) | Available | Building height context. Median imputed. |
| `location` | Categorical | `location` string (81 distinct location labels present in dataset) | Available | Dataset sub-market labels. One-Hot encoded with `handle_unknown='ignore'`. |
| `Furnishing` | Categorical | `Furnishing` string (Semi-Furnished, Unfurnished, Furnished) | Available | Physical fit-out status. One-Hot encoded. |
| `Transaction` | Categorical | `Transaction` string (Resale, New Property, Other) | Available | Market transaction type. One-Hot encoded. |
| `Status` | Categorical | `Status` string (Ready to Move, Other) | Available | Completion status. One-Hot encoded. |
| `facing` | Categorical | `facing` string (East, North, etc.) | Available | Directional orientation. One-Hot encoded. |
| `Ownership` | Categorical | `Ownership` string (Freehold, Leasehold, Co-operative, etc.) | Available | Title tenure. One-Hot encoded. |

---

## 6. Model Comparison & Test Evaluation Results

### Validation Set Comparison (9,788 rows, seed=42)

| Candidate Model | Val MAE (INR) | Val MAE (Lakh) | Val RMSE (Lakh) | Val R² | Baseline Improvement | Train Time |
|---|---|---|---|---|---|---|
| `dummy_median` (Baseline) | ₹6,207,976.09 | 62.08 L | 154.00 L | -0.0650 | Baseline | 0.29s |
| `ridge_log` | ₹3,991,697.55 | 39.92 L | 359.14 L | -4.7922 | +35.70% | 0.42s |
| `decision_tree_log` | ₹3,433,059.95 | 34.33 L | 98.07 L | 0.5681 | +44.70% | 0.67s |
| `random_forest_log` | ₹3,038,188.88 | 30.38 L | 91.90 L | 0.6207 | +51.06% | 3.10s |
| `hist_gradient_boosting_log` (Default) | ₹2,727,652.50 | 27.28 L | 84.90 L | 0.6763 | +56.06% | 2.34s |
| **`hist_gradient_boosting_log_tuned`** | **₹2,670,468.29** | **26.70 L** | **83.20 L** | **0.6891** | **+57.00%** | **Validation Tuning** |

### Final Untouched Test Set Evaluation (9,789 rows)

- **Dummy Baseline Test MAE:** INR 6,251,646.75 (62.52 Lakh), R² = -0.0581
- **Winning Model (`hist_gradient_boosting_log_tuned`) Test MAE:** **INR 2,693,927.27 (26.94 Lakh)**
- **Winning Model Test RMSE:** INR 8,517,820.69 (85.18 Lakh)
- **Winning Model Test R²:** **0.7104**
- **Test Median Absolute Error:** **INR 1,106,302.30 (11.06 Lakh)**
- **Relative MAE Improvement:** **+56.91%** (Target ≥10% **ACHIEVED**)
- **Negative Predictions:** 0
- **Non-finite Predictions:** 0

---

## 7. Versioned Artifact Specification

- **Artifact Path:** `ml/training/experiments/phase2/model_pipeline.joblib` (1,103,840 bytes, Git-ignored)
- **Metadata Path:** `ml/training/experiments/phase2/metadata.json` (8,839 bytes, Git-ignored)
- **Pipeline Structure:** Single serializable pipeline containing `PropertyFeatureExtractor`, `ColumnTransformer`, and `TransformedTargetRegressor(regressor=HistGradientBoostingRegressor, func=np.log1p, inverse_func=np.expm1)`.
- **Promotion Status:** Validated via `scripts/promote_model.py` with PASS status. Ready for Phase 3 standalone FastAPI inference service consumption.
