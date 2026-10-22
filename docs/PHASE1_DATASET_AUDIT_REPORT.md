# Phase 1 — Dataset Audit and Preparation Report

**Project:** Real Estate Price Prediction Platform — India
**Repository:** `OnkarGulhane/RealEstatePrediction`
**Governing Phase 0 Checkpoint:** `2a34367 chore(phase-0): align scaffold and verify project architecture`
**Date:** 2026-10-22
**Overall Status:** **PASS WITH WARNINGS**
*(Technical audit and deterministic preparation succeeded with 100% row reconciliation and 30/30 unit tests passing; WARNINGS remain regarding unverified dataset redistribution rights, repeated duplicate listings, and final feature set approval).*

---

## 1. Overall Status and Executive Summary

- **Overall Status:** `PASS WITH WARNINGS`
- **Phase Boundary Compliance:**
  - **Zero model training:** No machine learning models, regressions, ensembles, or feature selection for trained models were executed.
  - **Zero application/framework changes:** No Django endpoints, database migrations, frontend UI, or FastAPI inference endpoints were modified.
  - **Zero Git commits or pushes:** Working tree changes remain strictly local for owner inspection; no commits or pushes were made.
  - **Raw source immutability:** The raw dataset was inspected read-only and preserved byte-for-byte.
  - **Data leakage protection:** Raw and processed datasets are strictly ignored by `.gitignore` and excluded from version control.
  - **Phase 2 Gate:** Phase 2 has **NOT** started. The pipeline is stopped awaiting explicit owner sign-off.

---

## 2. Dataset Identity, Provenance, and Licence Audit

### 2.1 File Evidence on Local System

| Attribute | Measured Property / Value |
| :--- | :--- |
| **Source Archive Location** | `C:\Users\OMKAR\Downloads\archive.zip` |
| **Archive File Size** | 6,926,090 bytes (6.61 MB compressed) |
| **Archive Modification Timestamp** | 2026-10-21 20:12:48 |
| **Contained Member** | `house_prices.csv` (CRC32: `0x7128f731`) |
| **Uncompressed File Size** | 106,149,815 bytes (101.23 MB) |
| **Local Audit Read Path** | `ml/training/data/raw/house_prices.csv` |
| **Total Rows / Columns** | 187,531 rows, 21 columns |

### 2.2 Public Source Lead & Provenance Investigation

- **Matching Public Source:** [Kaggle: House Price by Juhi Bhojani](https://www.kaggle.com/datasets/juhibhojani/house-price)
- **Publisher / Author:** Juhi Bhojani
- **Dataset Title:** "House Price"
- **Stated Kaggle Licence:** `Community Data License Agreement - Sharing - Version 1.0` (CDLA-Sharing-1.0)
- **Access / Audit Date:** 2026-10-22
- **Evidence Linking Local File to Kaggle Source:**
  - File name matches exactly: `house_prices.csv`.
  - Schema matches 1:1 across all 21 columns (`Index`, `Title`, `Description`, `Amount(in rupees)`, `Price (in rupees)`, `location`, `Carpet Area`, `Status`, `Floor`, `Transaction`, `Furnishing`, `facing`, `overlooking`, `Society`, `Bathroom`, `Balcony`, `Car Parking`, `Ownership`, `Super Area`, `Dimensions`, `Plot Area`).
  - Row count matches exactly: 187,531 rows.
  - Value patterns match (e.g. `42 Lac`, `1.40 Cr`, `Call for Price`, `Ready to Move`, completely blank `Dimensions` and `Plot Area`).

### 2.3 Legal & Redistribution Assessment

- **Assessment:** **`UNVERIFIED / RESTRICTED FROM REDISTRIBUTION`**
- **Rationale:**
  1. Although the Kaggle uploader marked the dataset under `CDLA-Sharing-1.0`, the actual listing records, property descriptions, society names, and pricing text appear to have been scraped from Indian real estate listing aggregators (e.g., MagicBricks / 99acres).
  2. No upstream legal instrument or licensing permission from the original property portals or listing owners is evidenced in the dataset or metadata.
  3. Under project safety boundaries, scraping real estate listing portals without proven redistribution rights cannot be treated as public domain or redistributable.
- **Enforced Project Policy:**
  - The dataset and any derived subsets are strictly restricted to local technical evaluation.
  - Raw CSVs, processed CSVs, parquet files, and database dumps must remain permanently excluded from Git tracking via `.gitignore`.
  - No dataset excerpts or full-row samples may be committed to public repositories.

---

## 3. Reproducible Environment and Commands

The audit and preparation were executed on the local project environment using native Python 3.13.5 and standard libraries (`pandas`, `numpy`, `pytest`).

### 3.1 Verification Commands Executed

```bash
# 1. Establish Git baseline
git status --short
git log -1 --oneline
git diff --check

# 2. Verify dataset ignore rules
git check-ignore -v ml/training/data/raw/house_prices.csv ml/training/data/interim/prepared_properties.csv

# 3. Execute read-only data audit
python ml/training/scripts/validate_data.py --input-path ml/training/data/raw/house_prices.csv

# 4. Execute deterministic data preparation
python ml/training/scripts/prepare_data.py \
  --input-path ml/training/data/raw/house_prices.csv \
  --output-path ml/training/data/interim/prepared_properties.csv

# 5. Run test suite
python -m pytest ml/training/tests -v
backend\.venv\Scripts\python.exe -m pytest backend/tests -v
inference-service\.venv\Scripts\python.exe -m pytest inference-service/tests -v
npm.cmd --prefix frontend test
```

---

## 4. Measured Dataset Characteristics & Recomputed Statistics

### 4.1 Schema, Types, and Missingness Analysis

Total rows: **187,531** | Total columns: **21**

| Column Name | Stated / Detected Type | Null Count | Null % | Notes & Quality Findings |
| :--- | :--- | :--- | :--- | :--- |
| `Index` | `int64` | 0 | 0.00% | Sequential integer identifier (0 to 187,530). Excluded from model features. |
| `Title` | `object` (string) | 0 | 0.00% | High-level summary (e.g., "2 BHK Apartment for Sale in..."). |
| `Description` | `object` (string) | 0 | 0.00% | Natural language listing text. **Critical Leakage Risk:** Explicitly quotes asking price. |
| `Amount(in rupees)` | `object` (string) | 0 | 0.00% | Target column. Contains `Lac`, `Cr`, and `Call for Price`. |
| `Price (in rupees)` | `object` (string) | 17,994 | 9.60% | Calculated rate/sqft. **Critical Leakage Risk:** Derived from asking price / area. |
| `location` | `object` (string) | 0 | 0.00% | Micro-market/locality string (e.g., "Kharadi, Pune", "Thane West"). |
| `Carpet Area` | `object` (string) | 80,673 | 43.02% | Usable inner floor area with unit string. Exists in 106,858 rows. |
| `Status` | `object` (string) | 615 | 0.33% | Construction status. 99.67% is "Ready to Move" (near-constant). |
| `Floor` | `object` (string) | 7,054 | 3.76% | E.g., "4 out of 12", "Ground out of 4". Multi-part token. |
| `Transaction` | `object` (string) | 83 | 0.04% | "Resale" (144,383), "New Property" (42,884), "Other" (181). |
| `Furnishing` | `object` (string) | 2,903 | 1.55% | "Unfurnished" (101,842), "Semi-Furnished" (66,971), "Furnished" (15,815). |
| `facing` | `object` (string) | 70,203 | 37.44% | Cardinal direction (East, North-East, West, etc.). |
| `overlooking` | `object` (string) | 81,495 | 43.46% | View description ("Garden/Park, Pool, Main Road", etc.). |
| `Society` | `object` (string) | 109,653 | 58.47% | Residential society/complex name. Highly sparse. |
| `Bathroom` | `object` (string) | 830 | 0.44% | Bathroom count string ("1", "2", "3", "> 10"). |
| `Balcony` | `object` (string) | 29,006 | 15.47% | Balcony count string ("1", "2", "3", "> 10"). |
| `Car Parking` | `object` (string) | 103,357 | 55.11% | Covered/Open parking string. High missingness. |
| `Ownership` | `object` (string) | 39,475 | 21.05% | "Freehold" (136,544), "Leasehold" (6,000), "Co-operative Society" (3,284). |
| `Super Area` | `object` (string) | 107,685 | 57.42% | Built-up area including common spaces. Exists in 79,846 rows. |
| `Dimensions` | `float64` | **187,531** | **100.00%** | **Completely blank column.** Must be dropped. |
| `Plot Area` | `float64` | **187,531** | **100.00%** | **Completely blank column.** Must be dropped. |

---

### 4.2 Target `Amount(in rupees)` Parsing and Accounting

Every single row of the 187,531 input rows was deterministically audited and accounted for:

| Parsing Category | Count | % of Raw Total | Handling in Preparation Pipeline |
| :--- | :--- | :--- | :--- |
| **Valid `Lac` / `Lakh`** | 112,568 | 60.03% | Converted to numeric INR (`val * 100,000`) |
| **Valid `Cr` / `Crore`** | 65,279 | 34.81% | Converted to numeric INR (`val * 10,000,000`) |
| **Total Supervised Target (Valid)** | **177,847** | **94.84%** | **Included in prospective training set** |
| `Call for Price` | 9,684 | 5.16% | Classified explicitly; excluded from supervised target |
| Blank / NaN / Empty | 0 | 0.00% | None detected |
| Malformed / Unparseable | 0 | 0.00% | None detected (100% matched regex or 'Call for Price') |
| **Total Input Reconciled** | **187,531** | **100.00%** | **Zero unaccounted rows** |

#### Target Numeric Distribution (Valid 177,847 Rows in INR)
- **Minimum:** ₹100,000 (1.0 Lac)
- **25th Percentile:** ₹4,840,000 (48.4 Lac)
- **Median (50th Percentile):** ₹7,800,000 (78.0 Lac)
- **Mean:** ₹11,981,344.19 (~1.20 Cr)
- **75th Percentile:** ₹14,500,000 (1.45 Cr)
- **99th Percentile:** ₹70,000,000 (7.00 Cr)
- **Maximum:** ₹14,003,000,000 (~1,400.3 Cr)
  *(Note: Only 4 listings exceed 100 Cr; these are flagged for Phase 2 outlier review criteria and were NOT silently dropped).*

---

### 4.3 Area Conflation and Unit Audit

A critical finding was uncovered regarding the relationship between `Carpet Area` and `Super Area`:

| Metric | Measured Row Count | Notes |
| :--- | :--- | :--- |
| **Carpet Area Populated Only** | 106,858 | Usable floor area provided |
| **Super Area Populated Only** | 79,846 | Built-up area provided |
| **BOTH Carpet & Super Area Populated** | **0** | **Zero overlapping listings across entire dataset** |
| **NEITHER Carpet nor Super Area Populated** | **827** | Completely missing area metrics |
| **Total Rows** | **187,531** | `106,858 + 79,846 + 0 + 827 = 187,531` |

#### Unit Breakdown and Exact Arithmetic Reconciliation
- **Carpet Area Units (Total: 106,858):**
  - `sqft`: 100,428 listings (Verified factor: `1.0`)
  - `sqyrd`: 5,526 listings (Verified factor: `9.0`)
  - `sqm`: 894 listings (Verified factor: `10.76391`)
  - **Subtotal Verified Carpet Units:** `100,428 + 5,526 + 894 = 106,848`
  - Regional / Unverified Carpet Units (**10** listings): `marla` 3, `acre` 2, `kanal` 2, `ground` 1, `cent` 1, `bigha` 1.
  - **Exact Reconciliation:** `106,848 (verified) + 10 (regional) = 106,858 Carpet Area listings`.
- **Super Area Units (Total: 79,846):**
  - `sqft`: 75,406 listings (Verified factor: `1.0`)
  - `sqyrd`: 3,547 listings (Verified factor: `9.0`)
  - `sqm`: 873 listings (Verified factor: `10.76391`)
  - **Subtotal Verified Super Units:** `75,406 + 3,547 + 873 = 79,826`
  - Regional / Unverified Super Units (**20** listings): `marla` 8, `kanal` 4, `ground` 3, `biswa` 1, `aankadam` 1, `acre` 1, `hectare` 1, `cent` 1. *(Note: bigha does not occur in Super Area; it appears only in Carpet Area).*
  - **Exact Reconciliation:** `79,826 (verified) + 20 (regional) = 79,846 Super Area listings`.

#### Mutually Exclusive Area Partition Arithmetic
- Carpet Area Only: **106,858**
- Super Area Only: **79,846**
- BOTH Carpet and Super Area: **0**
- NEITHER Carpet nor Super Area: **827**
- **Sum Total:** `106,858 + 79,846 + 0 + 827 = 187,531` (100% exact match against raw CSV rows).

#### Audit Trail Note: One-Row Discrepancy Investigation & Resolution
During product owner review, a 1-row discrepancy was identified between the reported Super Area partition (79,846) and the draft regional unit sum (79,826 verified + 21 regional = 79,847). Direct inspection of the raw CSV and audit code revealed two contributing factors:
1. **Report Draft Typographical Transposition:** The draft text erroneously stated 21 regional units with inflated counts (`marla` 7 vs actual 8, `kanal` 3 vs actual 4, `biswa` 2 vs actual 1, `aankadam` 2 vs actual 1, and `bigha` 1 vs actual 0). The actual verified count of non-standard units in `Super Area` is exactly 20. Adding 20 to 79,826 verified units yields exactly 79,846.
2. **Regex Alphanumeric Parsing in Preparation Logic:** In `ml/training/src/real_estate_ml_training/clean.py`, `_AREA_PATTERN` originally matched only alphabetic characters (`[a-zA-Z\s]+`). Row index `171914` contains the value `'1970 biswa2'`, where the unit token contains a trailing numeric footnote digit (`2`). This caused `parse_area_field` to return `(None, None)` for that row, dropping `super_area_val` to `None` in the interim dataset and shifting row 171914 into the "Neither Area" count (yielding 79,845 Super Area and 828 Neither Area).
3. **Resolution Applied:**
   - Updated `clean.py` `_AREA_PATTERN` to `r"^\s*([\d,.]+)\s*([a-zA-Z0-9\s]+)?$"` with trailing footnote digit stripping in `parse_area_field`.
   - Added regression test `test_parse_area_field_alphanumeric_unit` in `ml/training/tests/test_data_rules.py`.
   - Regenerated local interim output `ml/training/data/interim/prepared_properties.csv`, restoring exact reconciliation: 106,858 Carpet Area, 79,846 Super Area, 0 Both, and 827 Neither Area.
   - Corrected all figures and tables in this report.


---

### 4.4 Duplicate Analysis

| Duplicate Scope | Exact Count | Proportion | Interpretation & Impact |
| :--- | :--- | :--- | :--- |
| **Full Row Duplicates (all 21 columns including Index)** | **0** | 0.00% | The `Index` column makes each raw CSV row syntactically unique. |
| **Duplicates Excluding Index (20 property columns)** | **119,339** | **63.64%** | Over 63% of rows in the CSV are repeated property records. |
| **Unique Property Record Signatures** | **68,192** | 36.36% | Exactly 68,192 unique property configurations exist across 187,531 rows. |
| **Repeating Group Membership** | 122,292 | 65.21% | 122,292 rows belong to duplicate clusters originating from 2,953 distinct properties. |

#### Deduplication Policy Recommendation:
- Blindly deduplicating drops 63.64% of the dataset, which may bias representation if identical units in massive high-rise developments were listed separately.
- Conversely, keeping all duplicates without grouped cross-validation will cause severe data leakage between training and validation splits.
- **Phase 1 Decision:** In compliance with strict boundaries, **no rows were deleted in the prepared output**. All 177,847 valid supervised rows are preserved locally, and the duplicate policy is formally deferred to the Product Owner for approval before Phase 2.

---

## 5. Cleaning and Preparation Rules Implemented

All preparation logic was implemented in `ml/training/src/real_estate_ml_training/clean.py` and executed via `ml/training/scripts/prepare_data.py`:

1. **Raw Immutability:** `ml/training/data/raw/house_prices.csv` is opened in read-only mode and is never modified.
2. **Identifier Isolation:** The raw `Index` column is excluded from candidate feature columns. A non-feature tracking field `source_row_index` is preserved for row-level audit reconciliation only.
3. **Blank Column Elimination:** `Dimensions` and `Plot Area` contain 187,531 nulls (100% missing). Both columns are dropped based on measured evidence.
4. **Target Leakage Elimination:**
   - `Price (in rupees)` is excluded because it represents rate/sqft derived directly from asking price and area.
   - `Description` is excluded because listing descriptions explicitly quote target asking prices in natural language.
5. **Target Parsing:** `Amount(in rupees)` is deterministically parsed to numeric INR for valid Lac and Cr formats. `Call for Price` (9,684 rows) is explicitly classified and excluded from the supervised modeling subset.
6. **Strict Area Separation:** `Carpet Area` and `Super Area` remain separate. Zero cross-imputation or conflation is performed.
7. **No In-Place Outlier Removal:** Observations with extreme prices (e.g., > 100 Cr) are flagged, not dropped.
8. **No Learned Transformations:** No scalers, one-hot encoders, or learned imputers were fit. All transformations are strictly deterministic, rule-based, and idempotent.

---

## 6. Output Artifacts and Git-Ignore Verification

| File Path | Description | Git Status / Ignore Check |
| :--- | :--- | :--- |
| `ml/training/data/raw/house_prices.csv` | Local raw source dataset (101.23 MB) | **Ignored** (`.gitignore:50:data/`) |
| `ml/training/data/interim/prepared_properties.csv` | Local prepared dataset (38.85 MB, 177,847 rows, 27 cols) | **Ignored** (`.gitignore:50:data/`) |
| `ml/training/src/real_estate_ml_training/audit.py` | Reusable data audit module | Tracked code |
| `ml/training/src/real_estate_ml_training/clean.py` | Deterministic preparation module | Tracked code |
| `ml/training/scripts/validate_data.py` | Audit CLI script | Tracked code |
| `ml/training/scripts/prepare_data.py` | Preparation CLI script | Tracked code |
| `ml/training/tests/test_data_rules.py` | Phase 1 unit test suite (30 tests) | Tracked code |

Verification output:
```text
.gitignore:50:data/    ml/training/data/raw/house_prices.csv
.gitignore:50:data/    ml/training/data/interim/prepared_properties.csv
```
No dataset files, archives, model artifacts, or secrets are tracked or staged.

---

## 7. Test Execution and Quality Results

### 7.1 Phase 1 Unit Tests (`ml/training/tests/test_data_rules.py`)

Command: `python -m pytest ml/training/tests -v`
**Result:** **30 passed in 0.47s**

- `test_parse_lac_standard`: Passed (42 Lac -> 4,200,000 INR)
- `test_parse_cr_standard`: Passed (1.40 Cr -> 14,000,000 INR)
- `test_parse_spacing_casing_plural_variants` [8 variants]: Passed
- `test_call_for_price`: Passed (classified explicitly, price is None)
- `test_blank_values` [4 variants]: Passed (None, "", "   ", NaN)
- `test_unsupported_or_malformed_not_silently_zero` [5 variants]: Passed
- `test_parse_area_field_valid`: Passed
- `test_convert_area_to_sqft_standard_units`: Passed (sqft, sqyrd, sqm)
- `test_regional_area_units_rejected`: Passed (marla, acre, kanal, ground, cent, bigha)
- `test_carpet_and_super_area_remain_separate`: Passed (no conflation)
- `test_raw_input_is_not_modified_in_place`: Passed
- `test_index_is_excluded_from_model_features`: Passed
- `test_blank_and_leakage_columns_are_excluded`: Passed
- `test_row_reconciliation_accounting`: Passed (100% row matching)
- `test_fail_clearly_on_missing_file`: Passed (raises FileNotFoundError)
- `test_duplicate_counts`: Passed

### 7.2 Regression Verification of Existing Project Services

- **Backend Test Suite:** `backend\.venv\Scripts\python.exe -m pytest backend/tests -v`
  **Result:** **3 passed in 0.16s** (Health check, Production settings with env, Production settings validation)
- **Inference Service Test Suite:** `inference-service\.venv\Scripts\python.exe -m pytest inference-service/tests -v`
  **Result:** **3 passed in 0.36s** (Liveness, Readiness 503 without model, Prediction 503 without model)
- **Frontend Test Suite:** `npm.cmd --prefix frontend test`
  **Result:** **2 passed in 141.97ms** (API client base URL handling)

---

## 8. Known Data Biases and Limitations

1. **Asking vs. Transaction Price Bias:** The target values are online listing / asking prices posted by sellers, brokers, or builders. In Indian real estate markets, negotiated final registry/transaction prices commonly differ by 5% to 20% from initial listing prices. The model predicts asking prices, not registered transaction prices.
2. **Area Non-Overlap (Carpet vs. Super Area):** In this dataset, listings report either Carpet Area or Super Area, never both. This requires careful handling during feature engineering in Phase 2 to avoid dropping 57% of the data.
3. **Portal Duplicate Inflation:** 63.64% of listings are duplicate property configurations posted multiple times to maximize portal visibility.
4. **Locality Granularity:** `location` contains free-text strings with varied formatting (e.g. "Sector 150, Noida", "Kharadi, Pune"). These require standardized micro-market parsing in later phases.
5. **Class Imbalance in Status:** 99.67% of non-null records are "Ready to Move", providing near-zero discriminatory signal across construction readiness.

---

## 9. Approved Product Owner Decisions for Phase 2

**Approval Date:** 2026-10-22
**Governing Authority:** Product Owner Review

The following four dataset and modeling policy decisions have been formally **APPROVED** by the product owner for execution in Phase 2:

1. **Exact Duplicates Policy (APPROVED):**
   - The primary training view in Phase 2 must exclude exact duplicate property rows when comparing all property columns except the unique `Index` identifier (68,192 unique property configurations retained).
   - The original raw CSV (`ml/training/data/raw/house_prices.csv`) and the existing full prepared output (`ml/training/data/interim/prepared_properties.csv`, 177,847 rows) must never be overwritten or deleted.
   - Phase 2 will report exact input/output counts and retain an auditable row/group mapping.
   - Phase 2 will evaluate whether a defensible grouping key exists for validation; no property identities will be invented. If no reliable grouping key exists, that limitation will be documented and claiming `GroupKFold` will be avoided.
   - *Status:* Approved policy for Phase 2. No deduplicated Phase 2 training view has been generated yet.

2. **Area Features Strategy (APPROVED):**
   - Keep `carpet_area_sqft` and `super_area_sqft` strictly separate.
   - Do **not** create a carpet-to-super-area ratio because the audited dataset has zero listings where both source fields are populated.
   - Plan separate indicators for raw-area presence and successful verified conversion so unverified regional units are not mistaken for absent source values.
   - *Status:* Approved policy for Phase 2 feature engineering.

3. **Regional / Ambiguous Units Handling (APPROVED):**
   - Do **not** discard the 30 records (10 in Carpet Area, 20 in Super Area) solely because their area units are unverified.
   - Preserve the rows and original raw unit/value for auditability.
   - Do not guess conversion factors. Leave the standardized square-foot value missing (`NaN`) when the unit cannot be verified, and document missing-value semantics.
   - *Status:* Implemented in Phase 1 preparation rules and approved for Phase 2 modeling.

4. **Dataset Provenance & Licensing (APPROVED):**
   - Keep raw, interim, and processed CSV data strictly local-only and excluded from Git tracking.
   - Do not commit or push any dataset files, archives, or redistributed excerpts.
   - The licence and provenance status remains formally designated as **`UNVERIFIED / RESTRICTED FROM REDISTRIBUTION`** unless official permission from the relevant source/rights holder is evidenced.
   - No alternative dataset will be substituted without explicit owner approval.
   - *Status:* Approved security and data-governance policy.

*Note: These decisions govern Phase 2 execution; they do not authorize starting Phase 2 now.*

---

## 10. Boundary Compliance Declaration

**Explicit Confirmations:**
- **No Machine Learning Model was trained.**
- **No feature selection for trained models was executed.**
- **No hyperparameter tuning was run.**
- **No deduplicated Phase 2 training view has been generated yet.**
- **All raw, interim, and processed dataset files remain strictly local and ignored by Git.**
- **Phase 2 has NOT started.**
- **Phase 1 audit and preparation work is finalized and checkpointed locally awaiting Phase 2 authorization.**
