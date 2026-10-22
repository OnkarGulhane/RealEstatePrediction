# Dataset & Machine Learning Specification (Starter Draft)

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Status | Audited & Approved for Phase 2 (Phase 1 Complete) |
| Dataset under audit | `house_prices.csv` (provided in user archive, 106,149,815 bytes) |
| Target Variable | Continuous Listing Price in Indian Rupees (`Amount(in rupees)`) |
| Approval Date | 22 October 2026 |
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
  - Duplicate listings excluding `Index`: **119,339 rows** (63.64% of CSV), leaving **68,192 unique property configurations** across 2,953 repeating property clusters.
- **100% Blank Columns (Dropped):** `Dimensions` (187,531 nulls) and `Plot Area` (187,531 nulls).
- **Target Leakage Fields (Excluded):** `Price (in rupees)` (rate/sqft derived from target) and `Description` (quotes asking prices verbatim).

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

## 4. Approved Phase 2 Dataset & Modeling Policies

**Approved by Product Owner on 22 October 2026:**

1. **Exact Duplicates Policy (APPROVED):**
   - The primary training view in Phase 2 must exclude exact duplicate property rows when comparing all property columns except the unique `Index` identifier (retaining the 68,192 unique property configurations).
   - The original raw CSV (`ml/training/data/raw/house_prices.csv`) and the existing full prepared dataset (`ml/training/data/interim/prepared_properties.csv`, 177,847 rows) will remain intact and will never be overwritten.
   - Phase 2 will report exact input/output counts and retain an auditable row/group mapping.
   - Phase 2 will evaluate whether a defensible grouping key exists for validation; no property identities will be invented. If no reliable grouping key exists, that limitation will be documented and claiming `GroupKFold` will be avoided.
   - *Status:* Approved policy for Phase 2. No deduplicated Phase 2 training view has been generated yet.

2. **Area Features Strategy (APPROVED):**
   - Keep `carpet_area_sqft` and `super_area_sqft` strictly separate.
   - Do **not** create a carpet-to-super-area ratio because the audited dataset has zero listings where both source fields are populated.
   - Plan separate indicators for raw-area presence and successful verified conversion so unverified regional units are not mistaken for absent source values.

3. **Regional / Ambiguous Units Handling (APPROVED):**
   - Do **not** discard the 30 records (10 in Carpet Area, 20 in Super Area) solely because their area units are unverified.
   - Preserve the rows and original raw unit/value for auditability.
   - Do not guess conversion factors. Leave the standardized square-foot value missing (`NaN`) when the unit cannot be verified, and document missing-value semantics.

4. **Dataset Provenance & Licensing (APPROVED):**
   - Keep raw, interim, and processed CSV data strictly local-only and excluded from Git tracking.
   - Do not commit or push any dataset files, archives, or redistributed excerpts.
   - The licence and provenance status remains formally designated as **`UNVERIFIED / RESTRICTED FROM REDISTRIBUTION`** unless official permission from the relevant source/rights holder is evidenced.
   - No alternative dataset will be substituted without explicit owner approval.

*Explicit Confirmation: No deduplicated training view has been generated yet and no model has been trained. Phase 2 has NOT started.*
