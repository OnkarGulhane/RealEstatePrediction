# Phase 2 — Offline Machine Learning Training and Evaluation Report

**Project:** Real Estate Price Prediction Platform — India<br>
**Repository:** `OnkarGulhane/RealEstatePrediction`<br>
**Execution Checkpoint:** Authorized by Product Owner after Phase 1 reconciliation push (`8957c7785e2cef1680d47fbfa7ae1b5bae60a4c8`)<br>
**Date:** 22 October 2026<br>
**Status:** **APPROVED** (Approved by Product Owner on 22 October 2026)

---

## 1. Executive Summary & Gate Status

Phase 2 offline machine learning training, feature engineering, validation-only hyperparameter tuning, and candidate model comparison have been completed in strict accordance with the approved architecture and safety boundaries.

- **Primary Supervised Training View:** Generated deterministically at `ml/training/data/processed/phase2_supervised_deduplicated.csv` with exactly **65,255 unique property configurations** (removing 112,592 duplicate occurrences from 177,847 valid supervised target records; 100% exact mathematical reconciliation).
- **Audit Mapping:** Preserved at `ml/training/data/processed/phase2_audit_mapping.csv` mapping every retained configuration to all original source indices and raw unverified units.
- **Model Comparison & Hyperparameter Tuning:** 5 regression candidates evaluated across identical 70/15/15 deterministic partitions. Bounded validation-only hyperparameter grid search performed on the leading gradient boosted tree candidate using training and validation partitions only (historical Treatment A exposure documented).
- **Winning Candidate:** **`HistGradientBoostingRegressor` (Tuned, log-target transform)**, achieving:
  - **Validation MAE:** INR 26.70 Lakh (+57.00% improvement over Dummy baseline, R² = 0.6891; improved from default 27.28 Lakh).
  - **Holdout Test MAE (Fixed Holdout Partition, 9,789 rows):** **INR 26.94 Lakh** (+56.91% improvement over Dummy baseline).
  - **Holdout Test R²:** **0.7104**.
  - **Holdout Test RMSE:** **INR 85.18 Lakh**.
  - **Holdout Test Median Absolute Error:** **INR 11.06 Lakh**.
  - **Proposed ≥10% MAE Target:** **ACHIEVED** (+56.91% vs +10.0% threshold).
  - **Negative or Non-Finite Predictions:** **0**.
- **Local Artifacts:** Versioned model pipeline (`model_pipeline.joblib`, 1.1 MB) and metadata (`metadata.json`, 8.8 KB) saved under gitignored `ml/training/experiments/phase2/`. Validated via `scripts/promote_model.py`.
- **Test Suite:** **75/75 unit tests passing** (`ml/training/tests`). Zero untracked datasets or model artifacts.

---

## 2. Initial Git / Entry-Gate Status

Prior to Phase 2 implementation and quality review, the mandatory entry gate was executed and verified:
1. `git status --short`: Empty (clean working tree).
2. `git branch --show-current`: `main`.
3. `git log -5 --oneline --decorate`:
   - `8957c77 (HEAD -> main, origin/main, origin/HEAD) fix(phase-1): reconcile supervised duplicate counts`
   - `1017f53 chore(phase-1): finalize dataset audit and record owner decisions`
   - `2a34367 chore(phase-0): align scaffold and verify project architecture`
   - `af95c59 chore: publish initial project scaffolding`
4. `git rev-parse HEAD`: `8957c7785e2cef1680d47fbfa7ae1b5bae60a4c8`.
5. `git rev-parse origin/main`: `8957c7785e2cef1680d47fbfa7ae1b5bae60a4c8`.
6. `git diff --check`: 0 warnings.
7. Local `main` and remote `origin/main` synchronized.

---

## 3. Deduplication Logic, Computed Row Counts & Reconciliation

### Deduplication Specification
- **Raw Input:** `ml/training/data/raw/house_prices.csv` (187,531 rows, 21 columns). Strictly immutable and read-only.
- **Target Filtering:** `Amount(in rupees)` parsed via deterministic regex.
  - Valid supervised targets: **177,847 rows** (112,568 Lac/Lakh + 65,279 Cr/Crore).
  - Excluded `Call for Price`: **9,684 rows**.
  - Blank / Unparseable: **0 rows**.
- **Deduplication Key:** All 20 property columns excluding the artificial unique `Index`:
  `['Title', 'Description', 'Amount(in rupees)', 'Price (in rupees)', 'location', 'Carpet Area', 'Status', 'Floor', 'Transaction', 'Furnishing', 'facing', 'overlooking', 'Society', 'Bathroom', 'Balcony', 'Car Parking', 'Ownership', 'Super Area', 'Dimensions', 'Plot Area']`
- **Output:** `ml/training/data/processed/phase2_supervised_deduplicated.csv` (65,255 rows) and `phase2_audit_mapping.csv` (65,255 rows).

### Exact Reconciliation Equations

$$\text{Total Raw Rows} = \text{Valid Supervised} + \text{Call for Price} + \text{Blank} + \text{Unparseable}$$
$$187{,}531 = 177{,}847 + 9{,}684 + 0 + 0 \quad (\mathbf{100\% \text{ exact}})$$

$$\text{Valid Supervised Rows} = \text{Unique Supervised Configurations} + \text{Duplicate Occurrences Removed}$$
$$177{,}847 = 65{,}255 + 112{,}592 \quad (\mathbf{100\% \text{ exact}})$$

$$\text{Raw Unique Configurations} = \text{Valid Unique} + \text{CFP Unique}$$
$$68{,}192 = 65{,}255 + 2{,}937 \quad (\mathbf{100\% \text{ exact}})$$

$$\text{Raw Duplicate Occurrences} = \text{Valid Duplicates} + \text{CFP Duplicates}$$
$$119{,}339 = 112{,}592 + 6{,}747 \quad (\mathbf{100\% \text{ exact}})$$

### Area Breakdown in Deduplicated View
- Carpet Area Only: **36,660 configurations**
- Super Area Only: **28,507 configurations**
- Both Areas Populated: **0 configurations** (Strict separation confirmed)
- Neither Area Populated: **88 configurations**
- Sum: $36{,}660 + 28{,}507 + 0 + 88 = 65{,}255$ (**100% exact match**).

---

## 4. Final Feature Schema, Indicator Policy & Parsing Audit

The fitted model pipeline consumes **22 total features** (16 numeric and 6 categorical), strictly excluding identifiers and target-leaking fields.

### Predictive Feature Table

| Feature Name | Type | Extraction & Transformation Logic | Availability at Inference | Indicator / Governance Compliance |
|---|---|---|---|---|
| `carpet_area_sqft` | Numeric | Parsed from `Carpet Area` (sqft, sqyrd, sqm converted). Imputed with median of training partition only. | Available | Kept strictly separate from super area. |
| `super_area_sqft` | Numeric | Parsed from `Super Area` (sqft, sqyrd, sqm converted). Imputed with median of training partition only. | Available | Kept strictly separate from carpet area. |
| `has_carpet_area` | Binary (0/1) | 1 if raw Carpet Area was provided, 0 otherwise. | Available | Distinguishes presence from absence. |
| `carpet_area_unit_verified` | Binary (0/1) | 1 if Carpet Area was converted using a verified standard unit (sqft, sqyrd, sqm), 0 if unverified/regional or absent. | Available | Distinguishes unverified provided units from absent values. |
| `has_super_area` | Binary (0/1) | 1 if raw Super Area was provided, 0 otherwise. | Available | Distinguishes presence from absence. |
| `super_area_unit_verified` | Binary (0/1) | 1 if Super Area was converted using a verified standard unit (sqft, sqyrd, sqm), 0 if unverified/regional or absent. | Available | Distinguishes unverified provided units from absent values. |
| `bhk` | Numeric | Parsed from `Title` (`(\d+)\s*bhk`, `studio` -> 1.0). 99.98% coverage. Median imputed. | Available | Core bedroom count. |
| `bathroom` | Numeric | Cleaned discrete count (1–10; `> 10` mapped to 10.0). Median imputed. | Available | Core amenity. |
| `bathroom_is_gt_10` | Binary (0/1) | 1 if raw source was literal `> 10` (open interval), 0 otherwise. | Available | Audited; flags top-coded dropdown records. |
| `balcony` | Numeric | Cleaned discrete count (1–10; `> 10` mapped to 10.0). Median imputed. | Available | Outdoor space. |
| `balcony_is_gt_10` | Binary (0/1) | 1 if raw source was literal `> 10` (open interval), 0 otherwise. | Available | Audited; flags top-coded dropdown records. |
| `parking_spaces` | Numeric | Valid vehicle spaces ($\le 20$ preserved exactly; $> 20$ assigned NaN and imputed via train-fitted median; qualitative text assigned 1.0; missing strings assigned 0.0). | Available | Preserves legitimate multi-car counts while treating magnitude $> 20$ as semantic-unknown. |
| `has_parking` | Binary (0/1) | 1 if parking information was populated, 0 if null/empty. | Available | Parking presence indicator. |
| `parking_count_ambiguous` | Binary (0/1) | 1 if parking text contained a flat/slot number $> 20$ (e.g. 402 Covered, 101 Covered), 0 otherwise. | Available | Flags slot number ambiguities. |
| `floor_num` | Numeric | Extracted from `Floor` (`X out of Y`: Ground -> 0, Basement -> -1). Median imputed. | Available | Elevation level. |
| `total_floors` | Numeric | Extracted from `Floor` (`X out of Y`: total building floors). Median imputed. | Available | Building height context. |
| `location` | Categorical | 81 distinct location labels/categories present in this dataset. OneHotEncoder(`handle_unknown='ignore'`). | Available | Dataset sub-market labels. |
| `Furnishing` | Categorical | `Semi-Furnished`, `Unfurnished`, `Furnished`, or `Unspecified`. OneHotEncoder. | Available | Interior furnishing status. |
| `Transaction` | Categorical | `Resale`, `New Property`, `Other`, or `Unspecified`. OneHotEncoder. | Available | Transaction nature. |
| `Status` | Categorical | `Ready to Move` vs `Other`. OneHotEncoder. | Available | Possession timeline. |
| `facing` | Categorical | Directional orientation (East, North, etc.). OneHotEncoder. | Available | Orientation. |
| `Ownership` | Categorical | Title tenure (Freehold, Leasehold, Co-operative, etc.). OneHotEncoder. | Available | Legal tenure structure. |

### Numeric Caps & Parsing Audit Details

1. **Bathroom & Balcony (`> 10`):**
   - Source data contains discrete integers 1 to 10, plus the exact string literal `"> 10"` originating from the portal UI dropdown.
   - Exact affected counts: **27 rows** for `Bathroom` (0.014%) and **13 rows** for `Balcony` (0.007%).
   - There were **zero raw integers > 10** in the dataset.
   - Treatment: Mapped `"> 10"` to 10.0 (the lower bound of the open interval) and added explicit binary indicators `bathroom_is_gt_10` and `balcony_is_gt_10`.
2. **Car Parking (Cap Audit, Boundary Cluster Sensitivity & Semantic Unknown Treatment):**
   - **Populated Row Accounting:**
     - **Deduplicated Supervised View (27,901 populated rows):**
       - $\le 20$: **27,602 rows** (98.93%) — legitimate counts of 1–20 spaces (villas, bungalows, independent houses).
       - $21–50$: **61 rows** (0.22%) — boundary cluster evaluated in sensitivity review.
       - $51–100$: **28 rows** (0.10%) — elevated identifiers/numbers.
       - $101–500$: **165 rows** (0.59%) — typical 3-digit unit or parking bay numbers (e.g., 101, 201, 304, 402).
       - $501–1000$: **45 rows** (0.16%) — typical high-floor unit/slot numbers (e.g., 501, 604, 702, 999).
       - $> 1000$: **0 rows** (0.00%).
       - Total $> 20$: **299 rows** (1.07% of populated parking).
     - **Raw Dataset (84,174 populated rows; inflated by scrape duplicates):**
       - $\le 20$: 82,957 rows; $21–50$: 636 rows; $51–100$: 33 rows; $101–500$: 495 rows; $501–1000$: 53 rows; $> 1000$: 0 rows. Total $> 20$: 1,217 rows.
   - **Deep Aggregate Breakdown of the 21–50 Boundary Cluster (61 deduplicated rows):**
     - **Parking Suffix / Type:** 39 Covered Only (63.9%), 22 Open Only (36.1%).
     - **Listing Title Typology:** 61 Flat / Apartment (100.0%). Zero villas, bungalows, or farmhouses.
     - **Price Tier Distribution:** 23 in $< 50$ Lakh (37.7%), 24 in 50L–1Cr (39.3%), 10 in 1–2Cr (16.4%), 4 in 2–5Cr (6.6%), 0 in $> 5$ Cr. 77.0% (47/61) are under ₹1 Crore; median asking price is ₹64.0 Lakh.
     - **Area Population:** 38 Carpet Area populated (62.3%), 23 Super Area populated (37.7%), 0 both, 0 neither (100% have valid floor areas).
     - **Geographic Spread:** Spans 32 distinct location labels (e.g., Gurgaon 6, Badlapur 4, Ranchi 4, Faridabad 4, Vadodara 4, Pune 3, Jaipur 3, Hyderabad 3, Goa 3).
   - **What Can and Cannot Be Inferred from the Data:**
     - *Can be inferred:* Having 21–50 private parking bays for a ₹64 Lakh 2 BHK residential apartment is physically implausible in Indian urban markets.
     - *Cannot be inferred:* The unstructured portal string cannot independently prove whether the seller intended a parking slot/bay number or entered an extreme count. Therefore, assuming that every value above 20 is an identifier is not treated as ground truth.
   - **Validation-Only Sensitivity Comparison (Train 45,678 rows vs Validation 9,788 rows, seed=42; Holdout Excluded from Comparison):**
     - Ambiguous rows in Training partition: 205 (0.45%); in Validation partition: 41 (0.42%).
     - **Treatment A (Current):** For $> 20$, set `parking_spaces = 1.0`, `has_parking = 1`, `parking_count_ambiguous = 1`.
       - Val MAE: **INR 26.70 Lakh** (₹2,669,974.40) | Val RMSE: **82.63 Lakh** | Val R²: **0.6934** | Val Med Error: **11.16 Lakh**
     - **Treatment B (Semantic-Unknown Alternative):** For $> 20$, set `parking_spaces = np.nan`, `has_parking = 1`, `parking_count_ambiguous = 1`; `parking_spaces` is median-imputed via `SimpleImputer` fitted strictly on training data.
       - Val MAE: **INR 26.70 Lakh** (₹2,670,468.29) | Val RMSE: **83.20 Lakh** | Val R²: **0.6891** | Val Med Error: **11.21 Lakh**
     - **Sensitivity Delta ($B - A$):**
       - MAE difference: $+₹493.89$ ($+0.0185\%$ / $+0.0049$ Lakh).
       - RMSE difference: $+0.57$ Lakh ($+0.69\%$).
       - R² difference: $-0.0042$.
       - *Finding:* The predictive difference between treatments is statistically negligible ($< 0.02\%$ MAE difference), reflecting the small sample size (0.42% of validation rows).
   - **Adopted Policy & Semantic Rationale:**
     - We adopt **Treatment B (Semantic-Unknown Alternative)** as the active default modeling convention.
     - *Active Default Enforcement:* Treatment B is implemented as the default parameterization across `PropertyFeatureExtractor(ambiguous_parking_as_nan=True)`, `train.py`, `evaluate.py`, and `promote_model.py`. The final candidate model artifact (`model_pipeline.joblib`) and metadata (`metadata.json`) were fully retrained and re-evaluated under Treatment B.
     - *Rationale:* Rather than asserting as ground truth that an unknown large number represents a factual count of 1.0 space, Treatment B formally treats the continuous magnitude as missing (`np.nan`), explicitly preserves presence (`has_parking = 1`) and ambiguity (`parking_count_ambiguous = 1`), and allows learned median imputation (fitted exclusively on the training partition) to populate the numeric input.
     - Full raw text is preserved in `phase2_audit_mapping.csv` for complete lineage.
     - *Metric Consistency:* All final validation, hyperparameter tuning, holdout test, and slice metrics presented in Sections 6 and 7 of this report are derived directly from this newly retrained Treatment B artifact. Old Treatment A test metrics were completely discarded and not carried forward.
3. **Location Coverage Description:**
   - Described strictly as **"81 distinct location labels/categories present in this dataset"** rather than "81 major Indian urban markets". Geographic generalization to unseen cities is not claimed and is safeguarded via `handle_unknown='ignore'` in the OneHotEncoder.

### Strictly Excluded Fields (Leakage Prevention)
1. **`Index`:** Artificial dataset row counter. Excluded.
2. **`Description`:** Free-form text containing verbatim asking prices (e.g., "available for an attractive price of INR 42 Lac"). Excluded.
3. **`Price (in rupees)`:** Direct rate per square foot derived directly from asking price. Excluded.
4. **`Dimensions` & `Plot Area`:** 100% missing (empty/null across all 187,531 rows). Dropped.
5. **`Amount(in rupees)`:** Target variable; modeled strictly as output, never as predictor.

---

## 5. Split Policy & Holdout Evaluation Discipline

### Grouping Key Feasibility Investigation
Before applying data splitting, proxy grouping keys were evaluated across the 65,255 unique configurations:
1. **`Society`:** 56.5% of unique listings (36,884 configurations) have no Society specified. For the 43.5% that have Society, grouping by society would lump entire townships into single clusters while leaving 56.5% of the data unclustered.
2. **`location + Title`:** Generic titles such as `"3 BHK Ready to Occupy Flat for sale Sector 85"` lump 175 independent developments together (over-grouping), while slight variations in phrasing for identical buildings fail to group (under-grouping).
3. **Conclusion:** No defensible, objective grouping key for physical properties exists in this scraped portal dataset. Claiming `GroupKFold` would fabricate non-existent physical boundaries.

### Adopted Split Strategy & Exact Holdout Call Flow
- **Method:** Deterministic, seeded train/validation/test split (`random_state=42`) after exact 20-column deduplication.
- **Partitions:**
  - **Train:** 45,678 rows (70.0%)
  - **Validation:** 9,788 rows (15.0%)
  - **Test (Holdout):** 9,789 rows (15.0%)
  - **Total:** 65,255 rows (100% exact).

### Exact Holdout Execution Flow (Pre-Freeze vs Post-Freeze & Historical Exposure Accounting)
1. **Pre-Freeze Training & Validation (Treatment B):**
   - Candidate models (Dummy, Ridge, Decision Tree, Random Forest, HistGradientBoosting) were fitted exclusively on the 45,678-row Training partition.
   - Model selection was decided strictly by Validation MAE across the 9,788-row Validation partition.
   - Bounded hyperparameter tuning (`run_validation_hyperparameter_tuning`) fitted 6 candidate configurations on the Training partition and selected the winner strictly using the Validation partition.
   - **For the final Treatment B pipeline, model selection and hyperparameter tuning were performed using training and validation data only; the holdout test partition was not consulted or used to guide tuning choices.**
2. **Post-Freeze Evaluation Reporting:**
   - Once the winning Treatment B model architecture and hyperparameters were completely frozen, holdout predictions were generated for reporting:
     - **In `scripts/train.py` Step [4/5]:** The frozen pipeline generated predictions on `test_df` to record top-level metrics into `ml/training/experiments/phase2/metadata.json`.
     - **In `scripts/evaluate.py` Steps [3-4/4]:** The standalone evaluation script loaded the saved pipeline artifact from disk, reproduced the identical test partition (`random_state=42`), and computed granular price-tier slices, BHK breakdowns, geographic segment slices, and residual distributions.
   - Both post-freeze reporting scripts evaluated the **identical frozen artifact** against the **identical test partition**. Zero metrics or insights from this holdout evaluation were fed back to modify features, hyperparameters, or model structure.
3. **Historical Holdout Exposure Limitation:**
   - The report must not claim or imply that this fixed holdout test set has never been inspected historically across the project lifecycle. An earlier Treatment A model iteration was evaluated on this exact deterministic split (`seed=42`) before the owner approved and authorized the Treatment B retrain.
   - While Treatment B choices were motivated by semantic validity and evaluated strictly via Train/Validation comparisons (with zero evidence of holdout-driven selection), the historical exposure of this split remains a documented limitation when interpreting these test metrics as a pristine first-time holdout estimate.
4. **Residual Near-Duplicate Leakage Limitation:**
   - Because physical apartment numbers and parcel identifiers are absent from web listings, residual near-duplicate leakage (e.g. identical floorplans on different floors or listings relisted with slight wording differences across random splits) cannot be formally excluded. This is recorded as a core dataset limitation.

---

## 6. Models Trained, Hyperparameter Tuning & Final Test Results

### Validation Set Comparison (9,788 rows, seed=42)

| Candidate Model | Val MAE (INR) | Val MAE (Lakh) | Val RMSE (Lakh) | Val R² | Improvement vs Baseline | Training Time |
|---|---|---|---|---|---|---|
| `dummy_median` (Baseline) | ₹6,207,976.09 | 62.08 L | 154.00 L | -0.0650 | Baseline | 0.29s |
| `ridge_log` | ₹3,991,697.55 | 39.92 L | 359.14 L | -4.7922 | +35.70% | 0.42s |
| `decision_tree_log` | ₹3,433,059.95 | 34.33 L | 98.07 L | 0.5681 | +44.70% | 0.67s |
| `random_forest_log` | ₹3,038,188.88 | 30.38 L | 91.90 L | 0.6207 | +51.06% | 3.10s |
| `hist_gradient_boosting_log` (Default) | ₹2,727,652.50 | 27.28 L | 84.90 L | 0.6763 | +56.06% | 2.34s |
| **`hist_gradient_boosting_log_tuned`** | **₹2,670,468.29** | **26.70 L** | **83.20 L** | **0.6891** | **+57.00%** | **Validation Tuning** |

### Ridge Regression Result Investigation
The `ridge_log` candidate exhibited a reasonable MAE (₹39.92 Lakh) but an extraordinarily large RMSE (₹359.14 Lakh) and a negative R² (-4.7922). Investigation revealed that linear regression fitted in $\log(1+y)$ space produces unbounded linear combinations when exposed to rare one-hot encoded location categories combined with large numerical area values. When exponentiated back via $\exp(\hat{y}) - 1$, these produce astronomical predictions (e.g. up to ₹311 Crore on properties actually priced at ₹3.5 Crore). Squaring these rare multi-hundred-crore errors produces residual sum-of-squares in excess of $10^{19}$, causing negative R² and massive RMSE. Tree-based regressors naturally bound leaf predictions within observed training price ranges, avoiding this failure mode entirely.

### Bounded Validation-Only Hyperparameter Tuning
Hyperparameter tuning was conducted on the leading gradient-boosted tree candidate using strictly the Training partition (45,678 rows) for fitting and the Validation partition (9,788 rows) for selection. For Treatment B, the holdout test partition was not used for candidate selection or hyperparameter tuning. Earlier Treatment A iterations had evaluated this same fixed split historically; that exposure remains a documented limitation (see Section 11, Remaining Risks & Boundaries).

- **Search Space:**
  - `max_iter`: [100, 150, 200]
  - `max_leaf_nodes`: [31, 45, 63]
  - `learning_rate`: [0.08, 0.1]
  - `min_samples_leaf`: [15, 20]
- **Tuning Trials Evaluated on Validation Set:**
  1. `{'max_iter': 100, 'max_leaf_nodes': 31, 'learning_rate': 0.1, 'min_samples_leaf': 20}`: Val MAE = 28.27 L, R² = 0.6561
  2. `{'max_iter': 150, 'max_leaf_nodes': 31, 'learning_rate': 0.1, 'min_samples_leaf': 20}`: Val MAE = 27.72 L, R² = 0.6667
  3. `{'max_iter': 150, 'max_leaf_nodes': 45, 'learning_rate': 0.1, 'min_samples_leaf': 20}`: Val MAE = 27.28 L, R² = 0.6763
  4. `{'max_iter': 150, 'max_leaf_nodes': 45, 'learning_rate': 0.08, 'min_samples_leaf': 20}`: Val MAE = 27.25 L, R² = 0.6787
  5. `{'max_iter': 200, 'max_leaf_nodes': 45, 'learning_rate': 0.1, 'min_samples_leaf': 20}`: Val MAE = 26.95 L, R² = 0.6873
  6. **`{'max_iter': 150, 'max_leaf_nodes': 63, 'learning_rate': 0.1, 'min_samples_leaf': 15}` (WINNER):** Val MAE = **26.70 L**, R² = **0.6891**
- **Outcome:** Validation MAE improved from 27.28 L to 26.70 L (+57.00% relative improvement over Dummy). Winning configuration was frozen and promoted for final evaluation.

### Fixed Holdout Test Partition Evaluation (9,789 rows)

The winning tuned model and Dummy baseline were evaluated on the final holdout test set:

| Evaluation Metric | Dummy Baseline | Winning Model (`hist_gradient_boosting_log_tuned`) | Relative Improvement | Target (≥10%) Status |
|---|---|---|---|---|
| **MAE (INR)** | ₹6,251,646.75 | **₹2,693,927.27** | **+56.91%** | **ACHIEVED (PASS)** |
| **MAE (Lakh)** | 62.52 Lakh | **26.94 Lakh** | +56.91% | Achieved |
| **RMSE (INR)** | ₹16,281,931.82 | **₹8,517,820.69** | +47.69% | Substantial reduction |
| **RMSE (Lakh)** | 162.82 Lakh | **85.18 Lakh** | +47.69% | Substantial reduction |
| **R² Score** | -0.0581 | **0.7104** | N/A | Strong variance explained |
| **Median Absolute Error** | ₹2,800,000.00 | **₹1,106,302.30 (11.06 L)** | +60.49% | Half of errors < 11.06 L |
| **Negative Predictions** | 0 | **0** | Perfect | 0 invalid predictions |
| **Non-finite Output** | 0 | **0** | Perfect | 0 NaN/Inf values |

---

## 7. Outlier, Residual & Segment Error Analysis

### Performance by Price Tier (Holdout Test Set)

| Price Tier | Test Sample Size | MAE (Lakh) | Median Absolute Error | Mean Percentage Error | Analysis |
|---|---|---|---|---|---|
| **< 50 Lakh (Affordable)** | 3,554 | 8.92 L | 6.31 L | 32.5% | Strong fit on volume listings; low absolute error |
| **50 Lakh - 1 Crore (Mid)** | 3,686 | 14.73 L | 10.87 L | 20.5% | Most accurate percentage tier; reliable pricing |
| **1 - 2 Crore (Upper Mid)** | 1,563 | 34.10 L | 27.17 L | 24.0% | Good stability; captures premium amenities |
| **2 - 5 Crore (Premium)** | 810 | 80.82 L | 65.04 L | 26.6% | Wider spread due to custom luxury features |
| **> 5 Crore (Luxury Outliers)** | 176 | 335.02 L | 184.82 L | 31.8% | Skewed by ultra-luxury listings (> 30 Cr) |

### Performance by BHK Tier

| BHK Configuration | Test Count | MAE (Lakh) | Median Actual Price |
|---|---|---|---|
| **1 BHK** | 874 | 10.31 L | 27.00 Lakh |
| **2 BHK** | 3,825 | 12.95 L | 47.90 Lakh |
| **3 BHK** | 4,142 | 27.05 L | 80.55 Lakh |
| **4 BHK** | 844 | 81.02 L | 210.00 Lakh |
| **5 BHK** | 80 | 217.40 L | 350.00 Lakh |
| **6 BHK** | 12 | 219.09 L | 410.00 Lakh |

### Performance Across Top 10 Geographic Locations

| Location | Test Count | MAE (Lakh) | Median Actual Price | Median Predicted Price | Alignment |
|---|---|---|---|---|---|
| **chennai** | 451 | 32.58 L | 65.00 Lakh | 67.66 Lakh | Strong median tracking |
| **ahmedabad** | 440 | 28.31 L | 73.00 Lakh | 75.42 Lakh | Strong median tracking |
| **hyderabad** | 432 | 31.05 L | 88.25 Lakh | 86.60 Lakh | Within 1.65 Lakh of median |
| **greater-noida** | 428 | 14.56 L | 63.55 Lakh | 61.12 Lakh | Excellent accuracy |
| **gurgaon** | 427 | 97.20 L | 190.00 Lakh | 203.01 Lakh | High-ticket market |
| **faridabad** | 424 | 16.12 L | 75.00 Lakh | 73.47 Lakh | Strong median tracking |
| **bangalore** | 419 | 43.25 L | 85.00 Lakh | 87.63 Lakh | Within 2.6 Lakh of median |
| **kolkata** | 414 | 26.90 L | 50.00 Lakh | 52.34 Lakh | Within 2.3 Lakh of median |
| **new-delhi** | 410 | 64.90 L | 165.00 Lakh | 166.18 Lakh | Within 1.2 Lakh of median |
| **jaipur** | 404 | 15.26 L | 50.00 Lakh | 52.84 Lakh | High precision |

### Residual Distribution & Bias Diagnosis ($e = y_{\text{true}} - y_{\text{pred}}$)
- **Mean Residual:** **+₹723,934.74 (+₹7.24 Lakh)**
- **Median Residual:** **-₹35,612.75 (-₹0.36 Lakh)**
- **25th Percentile:** **-₹1,020,156.07 (-₹10.20 Lakh)**
- **75th Percentile:** **+₹1,233,984.63 (+₹12.34 Lakh)**
- **10th Percentile:** **-₹2,503,686.13 (-₹25.04 Lakh)**
- **90th Percentile:** **+₹3,743,936.16 (+₹37.44 Lakh)**
- **Standard Deviation:** **INR 84.87 Lakh (₹8,487,001.10)**
- **Accurate Bias Characterization:**
  - With residual defined as actual minus predicted ($y_{\text{true}} - y_{\text{pred}}$), the **positive mean residual (+₹7.24 Lakh)** indicates that the model on average underpredicts property prices on this test set. This positive mean bias is heavily driven by the heavy right tail of luxury and ultra-luxury listings (> ₹5 Crore up to ₹140 Crore), where actual prices far exceed tree predictions.
  - In contrast, the **median residual (-₹0.36 Lakh)** is near zero and slightly negative, demonstrating that for typical, non-luxury properties (the middle 50% spanning -₹10.20L to +₹12.34L), predictions are well-balanced and median-centered.
  - The model must **not** be characterized as simply "unbiased"; rather, it exhibits low median bias on typical housing stock coupled with systematic conservatism on luxury tail assets.

---

## 8. Changed & Created File Paths

### Source Code & Scripts
- `ml/training/src/real_estate_ml_training/clean.py` — Added `build_phase2_deduplicated_view` with 20-col exact deduplication and audit trail mapping.
- `ml/training/src/real_estate_ml_training/features.py` — Implemented `PropertyFeatureExtractor` and `build_preprocessor` ColumnTransformer with case-insensitive column handling, parking cap, deterministic BHK extraction, and strict area separation.
- `ml/training/src/real_estate_ml_training/models.py` — Implemented `get_candidate_models`, `run_validation_hyperparameter_tuning`, `compute_metrics`, and `validate_candidate_artifact`.
- `ml/training/scripts/prepare_data.py` — Added `--phase2` CLI flag for generating deduplicated training view and audit mapping.
- `ml/training/scripts/train.py` — Full offline training, validation-only tuning, and model comparison script across 70/15/15 partitions.
- `ml/training/scripts/evaluate.py` — Comprehensive evaluation, holdout test metrics, and segment/residual analysis.
- `ml/training/scripts/promote_model.py` — Artifact promotion validation and smoke test.

### Automated Tests
- `ml/training/tests/test_phase2_training.py` — 43 unit tests for deduplication, feature extraction, parking/area indicators, unknown category handling, serialization, promotion validation, and Treatment B parking semantics.

### Documentation & Specifications
- `docs/IMPLEMENTATION_PLAN.md` — Updated Phase 0 and Phase 1 to APPROVED; Phase 2 to READY FOR REVIEW; marked completed tasks.
- `docs/DATASET_ML_SPEC.md` — Updated with Phase 2 feature schema (22 features), model comparison table, test set evaluation metrics, and artifact specification.
- `docs/OPEN_DECISIONS.md` — Updated Decision #3 (Duplicate Policy), Decision #5 (Area Basis), and Decision #6 (Location Policy) to EXECUTED IN PHASE 2.
- `docs/PHASE2_MODEL_EVALUATION_REPORT.md` — This comprehensive completion report.

---

## 9. Verification Commands & Test Evidence

| Command Executed | Exit Code | Result | Key Evidence |
|---|---|---|---|
| `python -m pytest ml/training/tests -v` | 0 | **75/75 PASS** (2.12s) | 32 Phase 1 tests + 43 Phase 2 tests green |
| `python ml/training/scripts/validate_data.py --data-path ml/training/data/raw/house_prices.csv` | 0 | **PASS** | 187,531 rows verified; 0 unaccounted rows |
| `python ml/training/scripts/prepare_data.py --phase2` | 0 | **PASS** | 65,255 unique configs; 112,592 duplicates; 100% cross-sum match |
| `python ml/training/scripts/train.py` | 0 | **PASS** | 5 models compared; validation tuning selected best; winning candidate versioned |
| `python ml/training/scripts/evaluate.py` | 0 | **PASS** | Holdout test MAE ₹26.94 L (+56.91% improvement); segment & residual analysis |
| `python ml/training/scripts/promote_model.py` | 0 | **PASS** | Artifact & metadata validated; smoke test prediction ₹81.12 L |
| `git diff --check` | 0 | **PASS** (Clean) | 0 whitespace or formatting warnings |
| `git check-ignore -v <6 paths>` | 0 | **PASS** | Raw, interim, processed CSVs, row mapping, model joblib, metadata all ignored |
| `git status --short` | 0 | **PASS** | Zero datasets, zero secrets, zero binary artifacts tracked |

---

## 10. Local Artifact Locations & Git-Ignore Proof

The generated machine learning pipeline artifact and metadata are stored in dedicated local directories that are strictly excluded from version control:

- **Trained Pipeline Artifact:** `ml/training/experiments/phase2/model_pipeline.joblib` (1,103,840 bytes)
- **Model Metadata:** `ml/training/experiments/phase2/metadata.json` (8,839 bytes)
- **Processed Deduplicated View:** `ml/training/data/processed/phase2_supervised_deduplicated.csv` (14,681,609 bytes)
- **Audit Mapping Table:** `ml/training/data/processed/phase2_audit_mapping.csv` (2,143,331 bytes)

### Proof of Git-Ignored Status
```text
$ git check-ignore -v \
    ml/training/data/raw/house_prices.csv \
    ml/training/data/interim/prepared_properties.csv \
    ml/training/data/processed/phase2_supervised_deduplicated.csv \
    ml/training/data/processed/phase2_audit_mapping.csv \
    ml/training/experiments/phase2/model_pipeline.joblib \
    ml/training/experiments/phase2/metadata.json

.gitignore:50:data/                    ml/training/data/raw/house_prices.csv
.gitignore:50:data/                    ml/training/data/interim/prepared_properties.csv
.gitignore:50:data/                    ml/training/data/processed/phase2_supervised_deduplicated.csv
.gitignore:50:data/                    ml/training/data/processed/phase2_audit_mapping.csv
.gitignore:60:ml/training/experiments/* ml/training/experiments/phase2/model_pipeline.joblib
.gitignore:60:ml/training/experiments/* ml/training/experiments/phase2/metadata.json
```

---

## 11. Remaining Risks & Boundaries

1. **Dataset Redistribution Restriction:** The dataset licence remains formally designated as **`UNVERIFIED / RESTRICTED FROM REDISTRIBUTION`**. No CSV files, data dumps, or binary model artifacts may be committed, published, or hosted publicly.
2. **Asking Price vs Transaction Price:** The model predicts seller asking/listing prices, which often include negotiation margins (typically 5–15% above final registry prices). This must be disclosed clearly in product UI disclaimers (Phase 5).
3. **Luxury Tail Volatility:** Listings exceeding ₹10 Crore exhibit high variance and wider confidence intervals due to idiosyncratic luxury amenities and custom architectural value.
4. **Residual Near-Duplicate Leakage:** Lack of defensible physical-property IDs means potential near-duplicate leakage across random partitions remains an explicit limitation.
5. **Historical Holdout Exposure:** Earlier Treatment A iterations were evaluated against this same fixed holdout test split (`seed=42`) before Treatment B was trained. Although final Treatment B model selection and hyperparameter tuning were conducted strictly on train/validation data without holdout feedback, historical exposure of this partition is an acknowledged limitation and should not be characterized as an unseen first-time test.
6. **Phase 3 Boundary:** No inference service endpoints or FastAPI HTTP serving has been implemented yet. Phase 3 is deferred pending product owner review and authorization.

---

## 12. Recommendation

**APPROVED BY PRODUCT OWNER (22 October 2026).**

Phase 2 offline machine learning training and evaluation met every defined criterion, achieved a +56.91% MAE improvement over baseline (far exceeding the ≥10% threshold), established a clean 75-test verification suite, and preserved strict dataset and code hygiene. Phase 3 (Independent Inference Service) is authorized.
