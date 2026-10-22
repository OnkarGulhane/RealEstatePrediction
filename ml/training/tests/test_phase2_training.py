"""
Unit tests for Phase 2 offline training, feature engineering, and model evaluation.

Verifies:
- Deduplication logic across 20 original columns excluding Index.
- Mathematical row accounting and reconciliation.
- Feature extraction determinism (BHK, Floor, Parking cap, counts).
- Target leakage prevention (no Index, Description, Price (in rupees), raw target).
- Separate Carpet and Super area handling with indicators.
- Unknown category resilience in preprocessing ColumnTransformer.
- Model candidate pipeline serialization, loading, and finite prediction smoke tests.
- Raw CSV immutability check.
"""
from __future__ import annotations

import json
import os
import tempfile
import numpy as np
import pandas as pd
import pytest
import joblib

from real_estate_ml_training.clean import (
    build_phase2_deduplicated_view,
    parse_target_price,
)
from real_estate_ml_training.features import (
    PropertyFeatureExtractor,
    build_preprocessor,
    extract_bhk,
    extract_floor_info,
    extract_parking_info,
    extract_parking_count,
    clean_count_field,
    ALL_MODEL_FEATURE_COLS,
    NUMERIC_FEATURE_COLS,
    CATEGORICAL_FEATURE_COLS,
)
from real_estate_ml_training.models import (
    compute_metrics,
    get_candidate_models,
    validate_candidate_artifact,
)


class TestDeduplicationAndRowReconciliation:
    """Verifies Phase 2 deduplicated training view creation and mathematical accounting."""

    def test_synthetic_deduplication_accounting(self):
        # Create synthetic dataset with known duplicates and targets
        data = {
            "Index": [1, 2, 3, 4, 5, 6],
            "Title": ["2 BHK Flat", "2 BHK Flat", "3 BHK Flat", "3 BHK Flat", "1 BHK Flat", "1 BHK Flat"],
            "Description": ["Desc A", "Desc A", "Desc B", "Desc B", "Desc C", "Desc C"],
            "Amount(in rupees)": ["50 Lac", "50 Lac", "1.2 Cr", "1.2 Cr", "Call for Price", "Call for Price"],
            "Price (in rupees)": ["5000", "5000", "8000", "8000", "Call", "Call"],
            "location": ["pune", "pune", "mumbai", "mumbai", "delhi", "delhi"],
            "Carpet Area": ["1000 sqft", "1000 sqft", None, None, "500 sqft", "500 sqft"],
            "Status": ["Ready to Move"] * 6,
            "Floor": ["2 out of 4"] * 6,
            "Transaction": ["Resale"] * 6,
            "Furnishing": ["Furnished"] * 6,
            "facing": ["East"] * 6,
            "overlooking": ["Main Road"] * 6,
            "Society": ["MySoc"] * 6,
            "Bathroom": ["2"] * 6,
            "Balcony": ["1"] * 6,
            "Car Parking": ["1 Covered"] * 6,
            "Ownership": ["Freehold"] * 6,
            "Super Area": [None, None, "1500 sqft", "1500 sqft", None, None],
            "Dimensions": [None] * 6,
            "Plot Area": [None] * 6,
        }
        raw_df = pd.DataFrame(data)
        dedup_df, audit_mapping_df, accounting = build_phase2_deduplicated_view(raw_df)

        # 6 raw rows: 4 valid target, 2 call for price
        assert accounting["total_raw_rows"] == 6
        assert accounting["valid_target_rows"] == 4
        assert accounting["call_for_price_rows"] == 2
        # Valid target unique configurations: 2 (rows 1/2 duplicate, rows 3/4 duplicate)
        assert accounting["valid_unique_configurations"] == 2
        assert accounting["valid_duplicate_occurrences"] == 2
        assert len(dedup_df) == 2
        assert len(audit_mapping_df) == 2
        assert audit_mapping_df["duplicate_count"].sum() == 4

    def test_dedup_view_does_not_mutate_raw_input(self):
        raw_df = pd.DataFrame({
            "Index": [1, 2],
            "Title": ["Flat A", "Flat A"],
            "Description": ["D", "D"],
            "Amount(in rupees)": ["40 Lac", "40 Lac"],
            "Price (in rupees)": ["4000", "4000"],
            "location": ["pune", "pune"],
            "Carpet Area": ["800 sqft", "800 sqft"],
            "Status": ["Ready to Move", "Ready to Move"],
            "Floor": ["1 out of 2", "1 out of 2"],
            "Transaction": ["Resale", "Resale"],
            "Furnishing": ["Unfurnished", "Unfurnished"],
            "facing": ["North", "North"],
            "overlooking": ["Park", "Park"],
            "Society": [None, None],
            "Bathroom": ["2", "2"],
            "Balcony": ["1", "1"],
            "Car Parking": [None, None],
            "Ownership": ["Freehold", "Freehold"],
            "Super Area": [None, None],
            "Dimensions": [None, None],
            "Plot Area": [None, None],
        })
        raw_copy = raw_df.copy()
        build_phase2_deduplicated_view(raw_df)
        pd.testing.assert_frame_equal(raw_df, raw_copy)


class TestFeatureExtractionRules:
    """Tests deterministic feature extractors and leakage prevention."""

    @pytest.mark.parametrize(
        "title,expected",
        [
            ("3 BHK Flat for sale in Pune", 3.0),
            ("2bhk apartment ready to move", 2.0),
            ("4 BHK Luxury Villa", 4.0),
            ("Studio apartment in Bangalore", 1.0),
            ("STUDIO for sale", 1.0),
            ("Commercial Shop for sale", np.nan),
            (None, np.nan),
            ("", np.nan),
        ],
    )
    def test_extract_bhk(self, title, expected):
        res = extract_bhk(title)
        if np.isnan(expected):
            assert np.isnan(res)
        else:
            assert res == expected

    @pytest.mark.parametrize(
        "floor_str,expected_floor,expected_total",
        [
            ("2 out of 4", 2.0, 4.0),
            ("Ground out of 3", 0.0, 3.0),
            ("Upper Basement out of 5", -1.0, 5.0),
            ("10 out of 20", 10.0, 20.0),
            ("Invalid floor", np.nan, np.nan),
            (None, np.nan, np.nan),
        ],
    )
    def test_extract_floor_info(self, floor_str, expected_floor, expected_total):
        f_num, tot_f = extract_floor_info(floor_str)
        if np.isnan(expected_floor):
            assert np.isnan(f_num)
        else:
            assert f_num == expected_floor
        if np.isnan(expected_total):
            assert np.isnan(tot_f)
        else:
            assert tot_f == expected_total

    @pytest.mark.parametrize(
        "parking_str,expected_spaces,expected_has_parking,expected_ambiguous",
        [
            ("1 Covered", 1.0, 1, 0),
            ("2 Covered", 2.0, 1, 0),
            ("1 Covered, 1 Open", 2.0, 1, 0),
            ("6 Covered", 6.0, 1, 0),    # Valid count > 5 preserved (up to 20)
            ("10 Open", 10.0, 1, 0),     # Valid villa/bungalow parking preserved
            ("20 Covered", 20.0, 1, 0),  # Exact upper boundary 20 preserved
            ("21 Covered", np.nan, 1, 1), # Exact boundary 21 flagged as ambiguous (Treatment B: NaN)
            ("34 Covered", np.nan, 1, 1), # Ambiguous 21-50 boundary cluster (Treatment B: NaN)
            ("402 Covered", np.nan, 1, 1), # High slot-like value flagged as ambiguous (Treatment B: NaN)
            ("Covered", 1.0, 1, 0),      # Qualitative presence without digit
            (None, 0.0, 0, 0),
            ("", 0.0, 0, 0),
            ("nan", 0.0, 0, 0),
            ("None", 0.0, 0, 0),
            ("null", 0.0, 0, 0),
        ],
    )
    def test_extract_parking_info(self, parking_str, expected_spaces, expected_has_parking, expected_ambiguous):
        spaces, has_p, amb = extract_parking_info(parking_str, max_valid_spaces=20.0, ambiguous_as_nan=True)
        if np.isnan(expected_spaces):
            assert np.isnan(spaces)
        else:
            assert spaces == expected_spaces
        assert has_p == expected_has_parking
        assert amb == expected_ambiguous

    def test_extract_parking_count_convenience(self):
        assert extract_parking_count("2 Covered") == 2.0
        assert np.isnan(extract_parking_count("402 Covered", ambiguous_as_nan=True))
        assert extract_parking_count("402 Covered", ambiguous_as_nan=False) == 1.0

    def test_parking_imputation_fitted_only_on_train_data(self):
        """Verifies that ambiguous parking (>20 -> NaN) is imputed using the train partition median only."""
        # Train partition with known parking counts: 2.0, 2.0, 2.0 -> median is 2.0
        train_raw = pd.DataFrame([
            {"location": "pune", "Car Parking": "2 Covered", "Furnishing": "Furnished", "Transaction": "Resale", "Status": "Ready to Move", "facing": "East", "Ownership": "Freehold", "carpet_area_sqft": 1000.0, "super_area_sqft": 1200.0, "has_carpet_area": 1, "carpet_area_unit_verified": 1, "has_super_area": 0, "super_area_unit_verified": 0, "bhk": 2.0, "bathroom": 2.0, "bathroom_is_gt_10": 0, "balcony": 1.0, "balcony_is_gt_10": 0, "parking_spaces": 2.0, "has_parking": 1, "parking_count_ambiguous": 0, "floor_num": 2.0, "total_floors": 4.0},
            {"location": "pune", "Car Parking": "2 Covered", "Furnishing": "Furnished", "Transaction": "Resale", "Status": "Ready to Move", "facing": "East", "Ownership": "Freehold", "carpet_area_sqft": 1000.0, "super_area_sqft": 1200.0, "has_carpet_area": 1, "carpet_area_unit_verified": 1, "has_super_area": 0, "super_area_unit_verified": 0, "bhk": 2.0, "bathroom": 2.0, "bathroom_is_gt_10": 0, "balcony": 1.0, "balcony_is_gt_10": 0, "parking_spaces": 2.0, "has_parking": 1, "parking_count_ambiguous": 0, "floor_num": 2.0, "total_floors": 4.0},
            {"location": "pune", "Car Parking": "2 Covered", "Furnishing": "Furnished", "Transaction": "Resale", "Status": "Ready to Move", "facing": "East", "Ownership": "Freehold", "carpet_area_sqft": 1000.0, "super_area_sqft": 1200.0, "has_carpet_area": 1, "carpet_area_unit_verified": 1, "has_super_area": 0, "super_area_unit_verified": 0, "bhk": 2.0, "bathroom": 2.0, "bathroom_is_gt_10": 0, "balcony": 1.0, "balcony_is_gt_10": 0, "parking_spaces": 2.0, "has_parking": 1, "parking_count_ambiguous": 0, "floor_num": 2.0, "total_floors": 4.0},
        ])

        # Test partition with ambiguous parking: '34 Covered' -> NaN
        test_raw = pd.DataFrame([{
            "location": "pune", "Car Parking": "34 Covered", "Furnishing": "Furnished", "Transaction": "Resale", "Status": "Ready to Move", "facing": "East", "Ownership": "Freehold", "carpet_area_sqft": 1000.0, "super_area_sqft": 1200.0, "has_carpet_area": 1, "carpet_area_unit_verified": 1, "has_super_area": 0, "super_area_unit_verified": 0, "bhk": 2.0, "bathroom": 2.0, "bathroom_is_gt_10": 0, "balcony": 1.0, "balcony_is_gt_10": 0, "parking_spaces": np.nan, "has_parking": 1, "parking_count_ambiguous": 1, "floor_num": 2.0, "total_floors": 4.0
        }])

        pre = build_preprocessor(scale_numeric=False)
        pre.fit(train_raw)

        test_trans = pre.transform(test_raw)
        # Find index of parking_spaces in NUMERIC_FEATURE_COLS
        from real_estate_ml_training.features import NUMERIC_FEATURE_COLS
        parking_idx = NUMERIC_FEATURE_COLS.index("parking_spaces")
        has_p_idx = NUMERIC_FEATURE_COLS.index("has_parking")
        amb_p_idx = NUMERIC_FEATURE_COLS.index("parking_count_ambiguous")

        # Imputed value must equal training partition median (2.0)
        assert test_trans[0, parking_idx] == 2.0
        # Presence and ambiguity flags must remain preserved
        assert test_trans[0, has_p_idx] == 1.0
        assert test_trans[0, amb_p_idx] == 1.0


    @pytest.mark.parametrize(
        "val,expected_count,expected_gt_10",
        [
            ("2", 2.0, 0),
            ("> 10", 10.0, 1),
            (3, 3.0, 0),
            (None, np.nan, 0),
            ("nan", np.nan, 0),
        ],
    )
    def test_clean_count_field(self, val, expected_count, expected_gt_10):
        cnt, gt_10 = clean_count_field(val)
        if np.isnan(expected_count):
            assert np.isnan(cnt)
        else:
            assert cnt == expected_count
        assert gt_10 == expected_gt_10

    def test_property_feature_extractor_columns(self):
        df = pd.DataFrame([{
            "Title": "3 BHK Apartment",
            "Floor": "4 out of 10",
            "Bathroom": "3",
            "Balcony": "2",
            "Car Parking": "1 Covered",
            "Carpet Area": "1200 sqft",
            "Super Area": None,
            "location": "pune",
            "Furnishing": "Semi-Furnished",
            "Transaction": "Resale",
            "Status": "Ready to Move",
            "facing": "East",
            "Ownership": "Freehold",
            # Leakage / unwanted columns to ensure they are excluded
            "Index": 999,
            "Description": "Price is 50 Lac",
            "Price (in rupees)": "5000",
            "Amount(in rupees)": "50 Lac",
        }])

        fe = PropertyFeatureExtractor()
        extracted = fe.transform(df)

        # Ensure all model feature columns exist
        for col in ALL_MODEL_FEATURE_COLS:
            assert col in extracted.columns, f"Missing expected feature col: {col}"

        # Ensure leakage columns are NOT in extracted
        assert "Index" not in extracted.columns
        assert "Description" not in extracted.columns
        assert "Price (in rupees)" not in extracted.columns
        assert "Amount(in rupees)" not in extracted.columns

        # Verify new indicators
        assert extracted["has_carpet_area"].iloc[0] == 1
        assert extracted["carpet_area_unit_verified"].iloc[0] == 1
        assert extracted["has_super_area"].iloc[0] == 0
        assert extracted["super_area_unit_verified"].iloc[0] == 0
        assert extracted["bathroom_is_gt_10"].iloc[0] == 0
        assert extracted["balcony_is_gt_10"].iloc[0] == 0
        assert extracted["has_parking"].iloc[0] == 1
        assert extracted["parking_count_ambiguous"].iloc[0] == 0


class TestModelPipelinesAndSmoke:
    """Tests model candidates and end-to-end preprocessing."""

    def test_candidate_models_suite(self):
        candidates = get_candidate_models(random_state=42)
        expected_models = [
            "dummy_median",
            "ridge_log",
            "decision_tree_log",
            "random_forest_log",
            "hist_gradient_boosting_log",
        ]
        for name in expected_models:
            assert name in candidates, f"Missing candidate: {name}"

    def test_preprocessing_handles_unknown_categories(self):
        train_df = pd.DataFrame([{
            "location": "pune",
            "Furnishing": "Furnished",
            "Transaction": "Resale",
            "Status": "Ready to Move",
            "facing": "East",
            "Ownership": "Freehold",
            "carpet_area_sqft": 1000.0,
            "super_area_sqft": np.nan,
            "has_carpet_area": 1,
            "carpet_area_unit_verified": 1,
            "has_super_area": 0,
            "super_area_unit_verified": 0,
            "bhk": 2.0,
            "bathroom": 2.0,
            "bathroom_is_gt_10": 0,
            "balcony": 1.0,
            "balcony_is_gt_10": 0,
            "parking_spaces": 1.0,
            "has_parking": 1,
            "parking_count_ambiguous": 0,
            "floor_num": 2.0,
            "total_floors": 4.0,
        }])

        test_df = pd.DataFrame([{
            "location": "unknown_future_city",
            "Furnishing": "brand_new_category",
            "Transaction": "Other",
            "Status": "UnknownStatus",
            "facing": "Diagonal",
            "Ownership": "NewOwnership",
            "carpet_area_sqft": 1100.0,
            "super_area_sqft": np.nan,
            "has_carpet_area": 1,
            "carpet_area_unit_verified": 1,
            "has_super_area": 0,
            "super_area_unit_verified": 0,
            "bhk": 3.0,
            "bathroom": 2.0,
            "bathroom_is_gt_10": 0,
            "balcony": 1.0,
            "balcony_is_gt_10": 0,
            "parking_spaces": 0.0,
            "has_parking": 0,
            "parking_count_ambiguous": 0,
            "floor_num": 1.0,
            "total_floors": 5.0,
        }])

        pre = build_preprocessor()
        pre.fit(train_df)
        # Should not crash on unknown categories
        transformed = pre.transform(test_df)
        assert np.all(np.isfinite(transformed))

    def test_pipeline_smoke_prediction(self):
        # Fit miniature candidate on 3 rows
        train_df = pd.DataFrame([
            {
                "Title": "2 BHK Flat",
                "Floor": "1 out of 4",
                "Bathroom": "2",
                "Balcony": "1",
                "Car Parking": "1 Covered",
                "Carpet Area": "900 sqft",
                "Super Area": None,
                "location": "pune",
                "Furnishing": "Furnished",
                "Transaction": "Resale",
                "Status": "Ready to Move",
                "facing": "East",
                "Ownership": "Freehold",
            },
            {
                "Title": "3 BHK Flat",
                "Floor": "3 out of 10",
                "Bathroom": "3",
                "Balcony": "2",
                "Car Parking": "2 Covered",
                "Carpet Area": None,
                "Super Area": "1500 sqft",
                "location": "mumbai",
                "Furnishing": "Semi-Furnished",
                "Transaction": "New Property",
                "Status": "Ready to Move",
                "facing": "North",
                "Ownership": "Freehold",
            },
        ])
        y_train = np.array([5_000_000.0, 15_000_000.0])

        candidates = get_candidate_models(random_state=42)
        model = candidates["hist_gradient_boosting_log"]
        model.fit(train_df, y_train)

        pred = model.predict(train_df)
        assert len(pred) == 2
        assert np.all(np.isfinite(pred))
        assert np.all(pred > 0)

        # Test joblib serialization and deserialization
        with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
            joblib.dump(model, f.name)
            loaded = joblib.load(f.name)
            pred2 = loaded.predict(train_df)
            assert np.allclose(pred, pred2)

    def test_candidate_promotion_validation(self):
        artifact_path = "ml/training/experiments/phase2/model_pipeline.joblib"
        metadata_path = "ml/training/experiments/phase2/metadata.json"
        if os.path.exists(artifact_path) and os.path.exists(metadata_path):
            report = validate_candidate_artifact(artifact_path, metadata_path)
            assert report["status"] == "PASS"
            assert "winning_candidate" in report
