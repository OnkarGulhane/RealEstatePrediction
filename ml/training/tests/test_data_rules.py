"""
Unit tests for Phase 1 dataset audit and preparation rules.

Verifies:
- Target price parsing (Lac, Cr, case/spacing variants, blanks, Call for Price, malformed strings)
- Unit standardization and strict separation of Carpet Area and Super Area
- Index and target-leakage column exclusion
- Raw input immutability
- Preparation accounting reconciliation
- Error handling on missing/malformed inputs
"""

import os
import tempfile
import pandas as pd
import numpy as np
import pytest

from real_estate_ml_training.clean import (
    parse_target_price,
    parse_area_field,
    convert_area_to_sqft,
    prepare_property_data,
    EXCLUDED_LEAKAGE_COLUMNS,
    EXCLUDED_BLANK_COLUMNS,
)
from real_estate_ml_training.audit import audit_dataset


class TestTargetPriceParsing:
    """Tests for deterministic parsing of Amount(in rupees)."""

    def test_parse_lac_standard(self):
        result = parse_target_price("42 Lac")
        assert result["status"] == "VALID"
        assert result["unit"] == "lac"
        assert result["price_inr"] == 4_200_000.0

    def test_parse_cr_standard(self):
        result = parse_target_price("1.40 Cr")
        assert result["status"] == "VALID"
        assert result["unit"] == "cr"
        assert result["price_inr"] == 14_000_000.0

    @pytest.mark.parametrize(
        "raw_text,expected_price,expected_unit",
        [
            ("42lac", 4_200_000.0, "lac"),
            ("  1.40  CR  ", 14_000_000.0, "cr"),
            ("85.5 Lakh", 8_550_000.0, "lac"),
            ("2.0 Crore", 20_000_000.0, "cr"),
            ("10 Lacs", 1_000_000.0, "lac"),
            ("1.25 Crores", 12_500_000.0, "cr"),
            ("75 LAKH", 7_500_000.0, "lac"),
            ("3.75 CRORE", 37_500_000.0, "cr"),
        ],
    )
    def test_parse_spacing_casing_plural_variants(self, raw_text, expected_price, expected_unit):
        result = parse_target_price(raw_text)
        assert result["status"] == "VALID"
        assert result["unit"] == expected_unit
        assert result["price_inr"] == expected_price

    def test_call_for_price(self):
        result = parse_target_price("Call for Price")
        assert result["status"] == "CALL_FOR_PRICE"
        assert result["price_inr"] is None

        result_lower = parse_target_price("call for price")
        assert result_lower["status"] == "CALL_FOR_PRICE"
        assert result_lower["price_inr"] is None

    @pytest.mark.parametrize("blank_val", [None, "", "   ", float("nan")])
    def test_blank_values(self, blank_val):
        result = parse_target_price(blank_val)
        assert result["status"] == "BLANK"
        assert result["price_inr"] is None

    @pytest.mark.parametrize(
        "malformed_val",
        [
            "100 USD",
            "invalid_amount",
            "12.5 UnknownUnit",
            "FREE",
            "$$$",
        ],
    )
    def test_unsupported_or_malformed_not_silently_zero(self, malformed_val):
        result = parse_target_price(malformed_val)
        assert result["status"] == "UNPARSEABLE"
        assert result["price_inr"] is None
        # Explicit check: Never silently convert malformed string to 0 or arbitrary number
        assert result["price_inr"] != 0.0


class TestAreaParsingAndSeparation:
    """Tests for Carpet Area and Super Area parsing, unit conversions, and isolation."""

    def test_parse_area_field_valid(self):
        val, unit = parse_area_field("1200 sqft")
        assert val == 1200.0
        assert unit == "sqft"

        val2, unit2 = parse_area_field("150.5 sqyrd")
        assert val2 == 150.5
        assert unit2 == "sqyrd"

        val3, unit3 = parse_area_field("85 sqm")
        assert val3 == 85.0
        assert unit3 == "sqm"

    def test_parse_area_field_alphanumeric_unit(self):
        # Regression test: alphanumeric unit strings with footnote digits (e.g. '1970 biswa2')
        val, unit = parse_area_field("1970 biswa2")
        assert val == 1970.0
        assert unit == "biswa"

    def test_convert_area_to_sqft_standard_units(self):
        # 1200 sqft -> 1200.0 sqft
        sqft, verified = convert_area_to_sqft(1200.0, "sqft")
        assert verified is True
        assert sqft == 1200.0

        # 100 sqyrd -> 900.0 sqft (1 sqyrd = 9 sqft)
        sqft_yrd, verified_yrd = convert_area_to_sqft(100.0, "sqyrd")
        assert verified_yrd is True
        assert sqft_yrd == 900.0

        # 100 sqm -> 1076.391 sqft (1 sqm = 10.76391 sqft)
        sqft_m, verified_m = convert_area_to_sqft(100.0, "sqm")
        assert verified_m is True
        assert round(sqft_m, 2) == 1076.39

    def test_regional_area_units_rejected(self):
        # Regional units must not be converted without rigorous evidence/justification
        for reg_unit in ["marla", "acre", "kanal", "ground", "cent", "bigha", "biswa", "aankadam", "hectare"]:
            sqft, verified = convert_area_to_sqft(10.0, reg_unit)
            assert verified is False
            assert sqft is None

    def test_carpet_and_super_area_remain_separate(self):
        sample_df = pd.DataFrame({
            "Index": [1, 2],
            "Amount(in rupees)": ["50 Lac", "1.2 Cr"],
            "Price (in rupees)": ["4000", "6000"],
            "Carpet Area": ["1000 sqft", None],
            "Super Area": [None, "1500 sqft"],
            "Dimensions": [None, None],
            "Plot Area": [None, None],
            "Description": ["Desc 1", "Desc 2"],
            "location": ["Loc A", "Loc B"],
            "Status": ["Ready to Move", "Ready to Move"],
        })

        prepared_df, stats = prepare_property_data(sample_df)

        # Both columns must exist distinctly in prepared dataframe
        assert "carpet_area_sqft" in prepared_df.columns
        assert "super_area_sqft" in prepared_df.columns

        # Verify no cross-imputation: Carpet Area for row 2 must remain NaN
        row1 = prepared_df.iloc[0]
        row2 = prepared_df.iloc[1]

        assert row1["carpet_area_sqft"] == 1000.0
        assert pd.isna(row1["super_area_sqft"])

        assert pd.isna(row2["carpet_area_sqft"])
        assert row2["super_area_sqft"] == 1500.0


class TestDataPreparationRules:
    """Tests for scoping, immutability, exclusions, and row accounting."""

    @pytest.fixture
    def sample_raw_df(self):
        return pd.DataFrame({
            "Index": [101, 102, 103, 104, 105],
            "Amount(in rupees)": [
                "42 Lac",
                "1.40 Cr",
                "Call for Price",
                "invalid_amt",
                None,
            ],
            "Price (in rupees)": ["4200", "7000", "N/A", "0", "0"],
            "Carpet Area": ["1000 sqft", None, "800 sqft", "500 sqft", None],
            "Super Area": [None, "2000 sqft", None, None, "1200 sqft"],
            "Dimensions": [None, None, None, None, None],
            "Plot Area": [None, None, None, None, None],
            "Description": [
                "42 Lac flat in nice locality",
                "1.40 Cr luxury apartment",
                "Call for price flat",
                "Unknown flat",
                "Blank flat",
            ],
            "location": ["City A", "City B", "City C", "City D", "City E"],
            "Status": ["Ready to Move", "Ready to Move", "Ready to Move", "Ready to Move", "Ready to Move"],
        })

    def test_raw_input_is_not_modified_in_place(self, sample_raw_df):
        original_copy = sample_raw_df.copy(deep=True)
        prepare_property_data(sample_raw_df)
        pd.testing.assert_frame_equal(sample_raw_df, original_copy)

    def test_index_is_excluded_from_model_features(self, sample_raw_df):
        prepared_df, _ = prepare_property_data(sample_raw_df)
        assert "Index" not in prepared_df.columns
        # source_row_index is kept solely for audit traceability
        assert "source_row_index" in prepared_df.columns

    def test_blank_and_leakage_columns_are_excluded(self, sample_raw_df):
        prepared_df, _ = prepare_property_data(sample_raw_df)
        for col in EXCLUDED_BLANK_COLUMNS:
            assert col not in prepared_df.columns
        for col in EXCLUDED_LEAKAGE_COLUMNS:
            assert col not in prepared_df.columns

    def test_row_reconciliation_accounting(self, sample_raw_df):
        prepared_df, stats = prepare_property_data(sample_raw_df)

        total_input = len(sample_raw_df)
        output_rows = len(prepared_df)
        call_for_price = stats["call_for_price_rows"]
        unparseable = stats["unparseable_target_rows"]
        blank = stats["blank_target_rows"]

        assert total_input == 5
        assert output_rows == 2  # 42 Lac and 1.40 Cr
        assert call_for_price == 1
        assert unparseable == 1
        assert blank == 1
        assert output_rows + call_for_price + unparseable + blank == total_input

    def test_fail_clearly_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            audit_dataset("non_existent_dataset_path_xyz_123.csv")


class TestDuplicateAnalysisReproducibility:
    """Tests that duplicate metrics calculations are deterministic and consistent."""

    def test_duplicate_counts(self):
        df = pd.DataFrame({
            "Index": [1, 2, 3, 4],
            "Amount(in rupees)": ["50 Lac", "50 Lac", "60 Lac", "50 Lac"],
            "location": ["Area A", "Area A", "Area B", "Area A"],
        })

        # Exact full row duplicate check (including Index):
        assert df.duplicated().sum() == 0

        # Duplicate check excluding Index:
        assert df.drop(columns=["Index"]).duplicated().sum() == 2

    def test_subset_duplicate_counts(self, tmp_path):
        csv_file = tmp_path / "test_dups.csv"
        df = pd.DataFrame({
            "Index": [1, 2, 3, 4, 5],
            "Amount(in rupees)": ["50 Lac", "50 Lac", "Call for Price", "Call for Price", "60 Lac"],
            "location": ["Area A", "Area A", "Area B", "Area B", "Area C"],
        })
        df.to_csv(csv_file, index=False)

        res = audit_dataset(str(csv_file))
        dups = res["duplicates"]
        assert dups["unique_property_combinations"] == 3
        assert dups["valid_target_rows"] == 3
        assert dups["valid_target_unique"] == 2
        assert dups["valid_target_duplicates"] == 1
        assert dups["call_for_price_rows"] == 2
        assert dups["call_for_price_unique"] == 1
        assert dups["call_for_price_duplicates"] == 1
        assert dups["valid_target_unique"] + dups["call_for_price_unique"] == dups["unique_property_combinations"]
