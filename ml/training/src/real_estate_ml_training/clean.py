"""
Data cleaning, target parsing, and area standardization module.
Phase 1: Deterministic, tested preparation rules.
Does not fit learned transformers or modify raw source data in place.
"""
from __future__ import annotations

import re
from typing import Any
import pandas as pd


# Regex patterns for deterministic parsing
_LAC_PATTERN = re.compile(
    r"^\s*([\d,.]+)\s*(?:lac|lakh|lacs|lakhs)\b",
    re.IGNORECASE
)
_CR_PATTERN = re.compile(
    r"^\s*([\d,.]+)\s*(?:cr|crore|crores)\b",
    re.IGNORECASE
)
_AREA_PATTERN = re.compile(
    r"^\s*([\d,.]+)\s*([a-zA-Z0-9\s]+)?$",
    re.IGNORECASE
)

# Verified conversion factors to square feet
# Conversion sources:
# - 1 square yard (sqyrd) = 9 square feet (sqft)
# - 1 square meter (sqm) = 10.7639104 square feet (sqft)
VERIFIED_AREA_FACTORS_TO_SQFT: dict[str, float] = {
    "sqft": 1.0,
    "sqyrd": 9.0,
    "sqm": 10.7639104,
}

EXCLUDED_BLANK_COLUMNS: list[str] = ["Dimensions", "Plot Area"]
EXCLUDED_LEAKAGE_COLUMNS: list[str] = ["Description", "Price (in rupees)"]



def parse_target_price(val: Any) -> dict[str, Any]:
    """
    Deterministically parses Amount(in rupees) string into numeric INR.

    Returns:
        dict with keys:
            - status: 'VALID' | 'CALL_FOR_PRICE' | 'BLANK' | 'UNPARSEABLE'
            - price_inr: float | None
            - raw_value: str
            - unit: 'lac' | 'cr' | None
    """
    if val is None or pd.isna(val):
        return {
            "status": "BLANK",
            "price_inr": None,
            "raw_value": "" if val is None else str(val),
            "unit": None,
        }

    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("nan", "null", "none"):
        return {
            "status": "BLANK",
            "price_inr": None,
            "raw_value": val_str,
            "unit": None,
        }

    if val_str.lower() == "call for price":
        return {
            "status": "CALL_FOR_PRICE",
            "price_inr": None,
            "raw_value": val_str,
            "unit": None,
        }

    # Match Lac / Lakh
    m_lac = _LAC_PATTERN.search(val_str)
    if m_lac:
        num_str = m_lac.group(1).replace(",", "")
        try:
            num = float(num_str)
            if num <= 0:
                return {
                    "status": "UNPARSEABLE",
                    "price_inr": None,
                    "raw_value": val_str,
                    "unit": "lac",
                }
            return {
                "status": "VALID",
                "price_inr": round(num * 100_000.0, 2),
                "raw_value": val_str,
                "unit": "lac",
            }
        except ValueError:
            return {
                "status": "UNPARSEABLE",
                "price_inr": None,
                "raw_value": val_str,
                "unit": "lac",
            }

    # Match Cr / Crore
    m_cr = _CR_PATTERN.search(val_str)
    if m_cr:
        num_str = m_cr.group(1).replace(",", "")
        try:
            num = float(num_str)
            if num <= 0:
                return {
                    "status": "UNPARSEABLE",
                    "price_inr": None,
                    "raw_value": val_str,
                    "unit": "cr",
                }
            return {
                "status": "VALID",
                "price_inr": round(num * 10_000_000.0, 2),
                "raw_value": val_str,
                "unit": "cr",
            }
        except ValueError:
            return {
                "status": "UNPARSEABLE",
                "price_inr": None,
                "raw_value": val_str,
                "unit": "cr",
            }

    return {
        "status": "UNPARSEABLE",
        "price_inr": None,
        "raw_value": val_str,
        "unit": None,
    }


def parse_area_field(val: Any) -> tuple[float | None, str | None]:
    """
    Extracts numeric magnitude and unit token from an area string.
    Does not convert units and does not conflate Carpet vs Super area.
    """
    if val is None or pd.isna(val):
        return None, None

    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("nan", "null", "none"):
        return None, None

    m = _AREA_PATTERN.search(val_str)
    if not m:
        return None, None

    num_part = m.group(1).replace(",", "")
    unit_raw = m.group(2).strip().lower() if m.group(2) else "sqft"
    # Normalize trailing digit footnotes (e.g. 'biswa2' -> 'biswa')
    unit_clean = re.sub(r"\d+$", "", unit_raw) or unit_raw

    try:
        val_float = float(num_part)
        return val_float, unit_clean
    except ValueError:
        return None, None


def convert_area_to_sqft(value: float | None, unit: str | None) -> tuple[float | None, bool]:
    """
    Converts known area units to square feet using deterministic, documented factors.
    Returns (converted_sqft, is_verified).
    If unit is unverified or regional (e.g. marla, kanal, ground, cent), returns (None, False).
    """
    if value is None or unit is None:
        return None, False

    clean_unit = unit.strip().lower()
    if clean_unit in VERIFIED_AREA_FACTORS_TO_SQFT:
        factor = VERIFIED_AREA_FACTORS_TO_SQFT[clean_unit]
        return round(value * factor, 4), True

    # Regional or unverified unit: do not guess conversion
    return None, False


def prepare_property_data(
    df: pd.DataFrame,
    include_call_for_price: bool = False
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Executes Phase 1 deterministic preparation on a DataFrame of raw listings:
    - Excludes Index from model feature fields.
    - Drops 100% blank columns (Dimensions, Plot Area).
    - Excludes target-leaking columns (Description, Price (in rupees)).
    - Parses Amount(in rupees) into numeric INR.
    - Separates Carpet Area and Super Area cleanly.
    - Excludes Call for Price / unparseable target rows from supervised set.
    """
    total_input_rows = len(df)
    cols = df.columns.tolist()

    # Step 1: Parse target
    target_results = [parse_target_price(v) for v in df["Amount(in rupees)"]]
    target_statuses = [r["status"] for r in target_results]
    target_inrs = [r["price_inr"] for r in target_results]
    target_units = [r["unit"] for r in target_results]

    accounting = {
        "total_input_rows": total_input_rows,
        "valid_target_rows": sum(1 for s in target_statuses if s == "VALID"),
        "call_for_price_rows": sum(1 for s in target_statuses if s == "CALL_FOR_PRICE"),
        "blank_target_rows": sum(1 for s in target_statuses if s == "BLANK"),
        "unparseable_target_rows": sum(1 for s in target_statuses if s == "UNPARSEABLE"),
    }

    # Step 2: Assemble prepared DataFrame
    prepared = pd.DataFrame()

    # Model identifiers: preserve original index in separate tracking column (not as model feature)
    if "Index" in cols:
        prepared["source_row_index"] = df["Index"].values

    # Target
    prepared["target_price_inr"] = target_inrs
    prepared["target_status"] = target_statuses
    prepared["target_unit"] = target_units

    # Area parsing: separate Carpet Area and Super Area
    carpet_parsed = [parse_area_field(v) for v in df.get("Carpet Area", [None] * total_input_rows)]
    super_parsed = [parse_area_field(v) for v in df.get("Super Area", [None] * total_input_rows)]

    prepared["carpet_area_raw"] = df.get("Carpet Area", [None] * total_input_rows)
    prepared["carpet_area_val"] = [p[0] for p in carpet_parsed]
    prepared["carpet_area_unit"] = [p[1] for p in carpet_parsed]

    carpet_sqft_conv = [convert_area_to_sqft(p[0], p[1]) for p in carpet_parsed]
    prepared["carpet_area_sqft"] = [c[0] for c in carpet_sqft_conv]
    prepared["carpet_area_unit_verified"] = [c[1] for c in carpet_sqft_conv]

    prepared["super_area_raw"] = df.get("Super Area", [None] * total_input_rows)
    prepared["super_area_val"] = [p[0] for p in super_parsed]
    prepared["super_area_unit"] = [p[1] for p in super_parsed]

    super_sqft_conv = [convert_area_to_sqft(p[0], p[1]) for p in super_parsed]
    prepared["super_area_sqft"] = [c[0] for c in super_sqft_conv]
    prepared["super_area_unit_verified"] = [c[1] for c in super_sqft_conv]

    # Property characteristics
    feature_candidates = [
        "Title", "location", "Status", "Floor", "Transaction",
        "Furnishing", "facing", "overlooking", "Society",
        "Bathroom", "Balcony", "Car Parking", "Ownership"
    ]
    for col in feature_candidates:
        if col in cols:
            prepared[col] = df[col].values

    # Accounting for area overlap
    has_carpet = prepared["carpet_area_val"].notnull()
    has_super = prepared["super_area_val"].notnull()
    accounting["carpet_area_count"] = int(has_carpet.sum())
    accounting["super_area_count"] = int(has_super.sum())
    accounting["both_areas_count"] = int((has_carpet & has_super).sum())
    accounting["neither_area_count"] = int((~has_carpet & ~has_super).sum())

    # Step 3: Filter for supervised modeling ready dataset
    if not include_call_for_price:
        prepared_supervised = prepared[prepared["target_status"] == "VALID"].copy()
    else:
        prepared_supervised = prepared.copy()

    accounting["output_rows"] = len(prepared_supervised)
    return prepared_supervised, accounting
