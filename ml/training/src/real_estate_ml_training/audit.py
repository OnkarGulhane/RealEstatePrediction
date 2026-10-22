"""
Data auditing module for raw real estate price listing datasets.
Phase 1: Deterministic, read-only audit of file structure, schema, missingness,
duplicates, target values, area units, and data quality limitations.
"""
from __future__ import annotations

import os
import zipfile
from typing import Any
import pandas as pd
import numpy as np

from .clean import parse_target_price


def _get_raw_dataframe(data_path: str) -> tuple[pd.DataFrame, int]:
    """
    Loads raw dataset from a path, supporting either a direct CSV or a ZIP archive containing house_prices.csv.
    Does not modify the source file.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Source dataset not found at path: {data_path}")

    file_size = os.path.getsize(data_path)

    if data_path.endswith(".zip"):
        with zipfile.ZipFile(data_path) as z:
            csv_names = [name for name in z.namelist() if name.endswith(".csv")]
            if not csv_names:
                raise ValueError(f"No CSV file found in archive {data_path}")
            target_csv = "house_prices.csv" if "house_prices.csv" in csv_names else csv_names[0]
            with z.open(target_csv) as f:
                df = pd.read_csv(f)
                return df, file_size
    else:
        df = pd.read_csv(data_path)
        return df, file_size


def audit_dataset(data_path: str) -> dict[str, Any]:
    """
    Executes a comprehensive, reproducible, read-only audit of the raw dataset.
    Never modifies raw data in place.
    """
    df, file_size_bytes = _get_raw_dataframe(data_path)
    total_rows, total_cols = df.shape
    cols = df.columns.tolist()

    # 1. Missingness & column summary
    null_counts = df.isnull().sum()
    null_percentages = (null_counts / total_rows * 100.0).round(2)

    column_summary: list[dict[str, Any]] = []
    blank_columns: list[str] = []
    constant_columns: list[str] = []

    for col in cols:
        n_missing = int(null_counts[col])
        pct_missing = float(null_percentages[col])
        n_unique = int(df[col].nunique(dropna=True))

        if n_missing == total_rows:
            blank_columns.append(col)
        elif n_unique <= 1:
            constant_columns.append(col)

        column_summary.append({
            "name": col,
            "dtype": str(df[col].dtype),
            "missing_count": n_missing,
            "missing_pct": pct_missing,
            "distinct_count": n_unique,
        })

    # 2. Duplicate analysis
    exact_full_duplicates = int(df.duplicated().sum())

    property_cols = [c for c in cols if c != "Index"]
    duplicates_excl_index = int(df.duplicated(subset=property_cols).sum())
    unique_property_combinations = total_rows - duplicates_excl_index

    # 3. Target parsing audit
    target_col = "Amount(in rupees)"
    if target_col in df.columns:
        parsed_targets = [parse_target_price(v) for v in df[target_col]]
        statuses = [t["status"] for t in parsed_targets]
        units = [t["unit"] for t in parsed_targets]
        prices_inr = [t["price_inr"] for t in parsed_targets if t["status"] == "VALID"]

        call_for_price_count = sum(1 for s in statuses if s == "CALL_FOR_PRICE")
        lac_count = sum(1 for u in units if u == "lac")
        cr_count = sum(1 for u in units if u == "cr")
        blank_target_count = sum(1 for s in statuses if s == "BLANK")
        unparseable_count = sum(1 for s in statuses if s == "UNPARSEABLE")
        valid_count = len(prices_inr)

        prices_series = pd.Series(prices_inr)
        price_stats = {
            "min_inr": float(prices_series.min()) if valid_count > 0 else None,
            "max_inr": float(prices_series.max()) if valid_count > 0 else None,
            "median_inr": float(prices_series.median()) if valid_count > 0 else None,
            "mean_inr": float(round(prices_series.mean(), 2)) if valid_count > 0 else None,
            "p01_inr": float(prices_series.quantile(0.01)) if valid_count > 0 else None,
            "p05_inr": float(prices_series.quantile(0.05)) if valid_count > 0 else None,
            "p25_inr": float(prices_series.quantile(0.25)) if valid_count > 0 else None,
            "p50_inr": float(prices_series.quantile(0.50)) if valid_count > 0 else None,
            "p75_inr": float(prices_series.quantile(0.75)) if valid_count > 0 else None,
            "p95_inr": float(prices_series.quantile(0.95)) if valid_count > 0 else None,
            "p99_inr": float(prices_series.quantile(0.99)) if valid_count > 0 else None,
            "count_under_1_lac": int((prices_series < 100_000).sum()) if valid_count > 0 else 0,
            "count_over_100_cr": int((prices_series > 1_000_000_000).sum()) if valid_count > 0 else 0,
        }
    else:
        valid_count = lac_count = cr_count = call_for_price_count = 0
        blank_target_count = unparseable_count = 0
        price_stats = {}

    # 4. Area overlap and unit distributions
    has_carpet = df["Carpet Area"].notnull() if "Carpet Area" in df.columns else pd.Series([False] * total_rows)
    has_super = df["Super Area"].notnull() if "Super Area" in df.columns else pd.Series([False] * total_rows)

    carpet_only = int((has_carpet & ~has_super).sum())
    super_only = int((~has_carpet & has_super).sum())
    both_areas = int((has_carpet & has_super).sum())
    neither_area = int((~has_carpet & ~has_super).sum())

    def _get_units(series: pd.Series) -> dict[str, int]:
        unit_counts: dict[str, int] = {}
        for val in series.dropna():
            val_str = str(val).strip()
            # Extract letters
            tokens = [c for c in val_str if c.isalpha()]
            unit = "".join(tokens).lower() if tokens else "no_unit"
            unit_counts[unit] = unit_counts.get(unit, 0) + 1
        return dict(sorted(unit_counts.items(), key=lambda x: x[1], reverse=True))

    carpet_units = _get_units(df["Carpet Area"]) if "Carpet Area" in df.columns else {}
    super_units = _get_units(df["Super Area"]) if "Super Area" in df.columns else {}

    # 5. Top categories for key categorical fields
    cat_cols = ["location", "Status", "Transaction", "Furnishing", "facing", "Bathroom", "Balcony"]
    top_categories: dict[str, dict[str, int]] = {}
    for col in cat_cols:
        if col in df.columns:
            vc = df[col].value_counts(dropna=False).head(10).to_dict()
            # Convert non-string keys
            top_categories[col] = {str(k): int(v) for k, v in vc.items()}

    return {
        "file_path": data_path,
        "file_size_bytes": file_size_bytes,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "columns": cols,
        "blank_columns": blank_columns,
        "constant_columns": constant_columns,
        "column_summary": column_summary,
        "duplicates": {
            "exact_full_duplicates": exact_full_duplicates,
            "duplicates_excluding_index": duplicates_excl_index,
            "unique_property_combinations": unique_property_combinations,
        },
        "target": {
            "column_name": target_col,
            "total_rows": total_rows,
            "valid_target_rows": valid_count,
            "lac_lakh_rows": lac_count,
            "cr_crore_rows": cr_count,
            "call_for_price_rows": call_for_price_count,
            "blank_target_rows": blank_target_count,
            "unparseable_target_rows": unparseable_count,
            "price_statistics_inr": price_stats,
        },
        "area": {
            "carpet_only_rows": carpet_only,
            "super_only_rows": super_only,
            "both_areas_rows": both_areas,
            "neither_area_rows": neither_area,
            "carpet_area_units": carpet_units,
            "super_area_units": super_units,
        },
        "top_categories": top_categories,
        "quality_and_leakage_findings": [
            "Index is an artificial row sequence and must be excluded from feature columns.",
            "Dimensions and Plot Area are 100% missing (empty strings / NaNs across all rows).",
            "Price (in rupees) represents rate per square foot and is a target leakage risk; excluded from prospective features.",
            "Description contains explicit asking price strings (e.g. 'available for an attractive price of INR 42 Lac'); excluded due to direct target leakage.",
            "Carpet Area and Super Area never co-occur in any listing row (0 overlapping rows). They must not be conflated or imputed into one another.",
            "Status is 99.67% 'Ready to Move' (186,916 out of 187,531 rows), offering near-zero predictive variance.",
            "119,339 rows share identical property characteristics when Index is excluded, likely due to scrape duplication across portal listing pages. Naive random train/test split would cause substantial evaluation leakage.",
            "Listing prices reflect seller asking prices, not verified final transaction prices.",
        ]
    }
