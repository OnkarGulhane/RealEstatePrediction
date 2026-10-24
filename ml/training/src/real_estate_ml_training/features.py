"""
Feature engineering and preprocessing pipelines for real estate price prediction.
Phase 2: Structured, deterministic feature extraction and scikit-learn transformers.

Rules:
- Strictly excludes target-leaking fields (Description, Price (in rupees), raw target).
- Extracts structured BHK from Title deterministically.
- Extracts floor_num and total_floors from Floor strings.
- Refined parking extraction: retains real counts up to 20; flags ambiguous slot/flat numbers (> 20) with parking_count_ambiguous=1.
- Refined bathroom/balcony: maps '> 10' to 10.0 (lower bound) and flags bathroom_is_gt_10 / balcony_is_gt_10.
- Keeps carpet_area_sqft and super_area_sqft strictly separate.
- Implements all 4 distinct area indicators: has_carpet_area, carpet_area_unit_verified, has_super_area, super_area_unit_verified.
- Safe unknown-category handling via OneHotEncoder(handle_unknown='ignore').
- Fits imputers and encoders ONLY on training partition.
"""
from __future__ import annotations

import re
from typing import Any
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from real_estate_ml_training.clean import (
    parse_area_field,
    convert_area_to_sqft,
    extract_sub_area_from_title,
)

# Deterministic regex patterns
_BHK_PATTERN = re.compile(r"(\d+)\s*bhk", re.IGNORECASE)
_STUDIO_PATTERN = re.compile(r"\bstudio\b", re.IGNORECASE)
_FLOOR_PATTERN = re.compile(
    r"^\s*(\d+|ground|lower basement|upper basement|basement)\s*out of\s*(\d+)",
    re.IGNORECASE
)
_PARKING_PATTERN = re.compile(r"(\d+)\s*(?:covered|open)?", re.IGNORECASE)

NUMERIC_FEATURE_COLS: list[str] = [
    "carpet_area_sqft",
    "super_area_sqft",
    "has_carpet_area",
    "carpet_area_unit_verified",
    "has_super_area",
    "super_area_unit_verified",
    "bhk",
    "bathroom",
    "bathroom_is_gt_10",
    "balcony",
    "balcony_is_gt_10",
    "parking_spaces",
    "has_parking",
    "parking_count_ambiguous",
    "floor_num",
    "total_floors",
]

CATEGORICAL_FEATURE_COLS: list[str] = [
    "location",
    "sub_area",
    "Furnishing",
    "Transaction",
    "Status",
    "facing",
    "Ownership",
]

ALL_MODEL_FEATURE_COLS: list[str] = NUMERIC_FEATURE_COLS + CATEGORICAL_FEATURE_COLS


def extract_bhk(title: Any) -> float:
    """Deterministically extracts BHK count from Title string."""
    if not isinstance(title, str) or not title.strip():
        return np.nan
    m = _BHK_PATTERN.search(title)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return np.nan
    if _STUDIO_PATTERN.search(title):
        return 1.0
    return np.nan


def extract_floor_info(floor_val: Any) -> tuple[float, float]:
    """
    Extracts (floor_num, total_floors) from floor string like '2 out of 4', 'Ground out of 3'.
    Returns (np.nan, np.nan) if unparseable or blank.
    """
    if not isinstance(floor_val, str) or not floor_val.strip():
        return np.nan, np.nan
    m = _FLOOR_PATTERN.search(floor_val.strip())
    if not m:
        return np.nan, np.nan

    f_str = m.group(1).lower()
    if f_str == "ground":
        floor_num = 0.0
    elif "basement" in f_str:
        floor_num = -1.0
    else:
        try:
            floor_num = float(f_str)
        except ValueError:
            floor_num = np.nan

    try:
        total_floors = float(m.group(2))
    except ValueError:
        total_floors = np.nan

    return floor_num, total_floors


def extract_parking_info(
    parking_val: Any,
    max_valid_spaces: float = 20.0,
    ambiguous_as_nan: bool = True,
) -> tuple[float, int, int]:
    """
    Extracts (parking_spaces, has_parking, parking_count_ambiguous) from Car Parking string.
    - Retains valid numeric counts up to max_valid_spaces (default 20.0).
    - If numbers > max_valid_spaces occur (e.g. '402 Covered', '101 Covered', '34 Covered'),
      the data cannot reliably distinguish whether the number represents a parking bay / unit
      identifier or an unusually high count.
      - If ambiguous_as_nan=True (Treatment B, semantic-unknown): sets parking_spaces=np.nan (unknown count),
        preserving has_parking=1 and parking_count_ambiguous=1, allowing learned median imputation on train data.
      - If ambiguous_as_nan=False (Treatment A): sets parking_spaces=1.0, has_parking=1, parking_count_ambiguous=1.
    - If NaN, empty, or 'None'/'nan'/'null': returns (0.0, 0, 0).
    - If qualitative string without numbers (e.g. 'Covered'): returns (1.0, 1, 0).
    """
    if not isinstance(parking_val, str) or not parking_val.strip():
        return 0.0, 0, 0
    s = parking_val.strip()
    if s.lower() in ("nan", "null", "none"):
        return 0.0, 0, 0
    matches = _PARKING_PATTERN.findall(s)
    if not matches:
        return 1.0, 1, 0
    try:
        nums = [int(x) for x in matches]
        max_num = max(nums)
        if max_num > max_valid_spaces:
            # Ambiguous count / bay number: treat magnitude as unknown (NaN) while preserving presence & flag
            return (np.nan if ambiguous_as_nan else 1.0), 1, 1
        total = sum(nums)
        return float(total), 1, 0
    except ValueError:
        return (np.nan if ambiguous_as_nan else 1.0), 1, 1


def extract_parking_count(
    parking_val: Any,
    max_valid_spaces: float = 20.0,
    ambiguous_as_nan: bool = True,
) -> float:
    """Convenience helper returning parsed parking spaces count."""
    return extract_parking_info(
        parking_val,
        max_valid_spaces=max_valid_spaces,
        ambiguous_as_nan=ambiguous_as_nan,
    )[0]



def clean_count_field(val: Any) -> tuple[float, int]:
    """
    Cleans discrete count fields like Bathroom or Balcony.
    Returns (count_float, is_gt_10_flag).
    - If '> 10': returns (10.0, 1) (lower bound of portal dropdown interval, flagged).
    - If numeric string/int: returns (float(val), 0).
    - If missing/NaN: returns (np.nan, 0).
    """
    if val is None or pd.isna(val):
        return np.nan, 0
    s = str(val).strip()
    if not s or s.lower() in ("nan", "null", "none"):
        return np.nan, 0
    if s == "> 10":
        return 10.0, 1
    try:
        return float(s), 0
    except ValueError:
        return np.nan, 0


class PropertyFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Extracts clean numeric and categorical feature columns from raw listing records.
    Produces ONLY the approved predictive features, dropping all identifiers and leakage fields.
    """

    def __init__(
        self,
        max_valid_parking: float = 20.0,
        ambiguous_parking_as_nan: bool = True,
    ):
        self.max_valid_parking = max_valid_parking
        self.ambiguous_parking_as_nan = ambiguous_parking_as_nan

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def _get_col(self, X: pd.DataFrame, *candidates: str) -> pd.Series | None:
        """Finds first matching column name from candidates (case-insensitive)."""
        col_map = {str(c).lower().strip(): c for c in X.columns}
        for cand in candidates:
            cand_low = cand.lower().strip()
            if cand_low in col_map:
                return X[col_map[cand_low]]
        return None

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        out = pd.DataFrame(index=X.index)

        # 1. Area features: check if already standardized or parse if raw
        carpet_sqft_s = self._get_col(X, "carpet_area_sqft")
        carpet_raw_s = self._get_col(X, "Carpet Area", "carpet_area_raw", "carpet_area")
        carpet_ver_s = self._get_col(X, "carpet_area_unit_verified")
        has_carpet_s = self._get_col(X, "has_carpet_area")

        if carpet_sqft_s is not None:
            out["carpet_area_sqft"] = pd.to_numeric(carpet_sqft_s, errors="coerce")
        elif carpet_raw_s is not None:
            carpet_parsed = [parse_area_field(v) for v in carpet_raw_s]
            out["carpet_area_sqft"] = [convert_area_to_sqft(p[0], p[1])[0] for p in carpet_parsed]
        else:
            out["carpet_area_sqft"] = np.nan

        if has_carpet_s is not None:
            out["has_carpet_area"] = pd.to_numeric(has_carpet_s, errors="coerce").fillna(0).astype(int)
        elif carpet_raw_s is not None:
            out["has_carpet_area"] = carpet_raw_s.notnull().astype(int)
        else:
            out["has_carpet_area"] = out["carpet_area_sqft"].notnull().astype(int)

        if carpet_ver_s is not None:
            out["carpet_area_unit_verified"] = pd.to_numeric(carpet_ver_s, errors="coerce").fillna(0).astype(int)
        elif carpet_raw_s is not None:
            carpet_parsed = [parse_area_field(v) for v in carpet_raw_s]
            out["carpet_area_unit_verified"] = [int(convert_area_to_sqft(p[0], p[1])[1]) for p in carpet_parsed]
        else:
            out["carpet_area_unit_verified"] = out["carpet_area_sqft"].notnull().astype(int)

        # Super area features
        super_sqft_s = self._get_col(X, "super_area_sqft")
        super_raw_s = self._get_col(X, "Super Area", "super_area_raw", "super_area")
        super_ver_s = self._get_col(X, "super_area_unit_verified")
        has_super_s = self._get_col(X, "has_super_area")

        if super_sqft_s is not None:
            out["super_area_sqft"] = pd.to_numeric(super_sqft_s, errors="coerce")
        elif super_raw_s is not None:
            super_parsed = [parse_area_field(v) for v in super_raw_s]
            out["super_area_sqft"] = [convert_area_to_sqft(p[0], p[1])[0] for p in super_parsed]
        else:
            out["super_area_sqft"] = np.nan

        if has_super_s is not None:
            out["has_super_area"] = pd.to_numeric(has_super_s, errors="coerce").fillna(0).astype(int)
        elif super_raw_s is not None:
            out["has_super_area"] = super_raw_s.notnull().astype(int)
        else:
            out["has_super_area"] = out["super_area_sqft"].notnull().astype(int)

        if super_ver_s is not None:
            out["super_area_unit_verified"] = pd.to_numeric(super_ver_s, errors="coerce").fillna(0).astype(int)
        elif super_raw_s is not None:
            super_parsed = [parse_area_field(v) for v in super_raw_s]
            out["super_area_unit_verified"] = [int(convert_area_to_sqft(p[0], p[1])[1]) for p in super_parsed]
        else:
            out["super_area_unit_verified"] = out["super_area_sqft"].notnull().astype(int)

        # 2. BHK from direct column or Title
        bhk_s = self._get_col(X, "bhk")
        title_s = self._get_col(X, "Title", "title")
        if bhk_s is not None:
            out["bhk"] = pd.to_numeric(bhk_s, errors="coerce")
        elif title_s is not None:
            out["bhk"] = [extract_bhk(v) for v in title_s]
        else:
            out["bhk"] = np.nan

        # 3. Bathroom & Balcony with > 10 flag
        bath_s = self._get_col(X, "Bathroom", "bathrooms", "bathroom")
        if bath_s is not None:
            bath_tuples = [clean_count_field(v) for v in bath_s]
            out["bathroom"] = [t[0] for t in bath_tuples]
            out["bathroom_is_gt_10"] = [t[1] for t in bath_tuples]
        else:
            out["bathroom"] = np.nan
            out["bathroom_is_gt_10"] = 0

        balc_s = self._get_col(X, "Balcony", "balconies", "balcony")
        if balc_s is not None:
            balc_tuples = [clean_count_field(v) for v in balc_s]
            out["balcony"] = [t[0] for t in balc_tuples]
            out["balcony_is_gt_10"] = [t[1] for t in balc_tuples]
        else:
            out["balcony"] = np.nan
            out["balcony_is_gt_10"] = 0

        # 4. Parking info
        park_s = self._get_col(X, "Car Parking", "parking_spaces", "parking", "car_parking")
        if park_s is not None:
            max_park = getattr(self, "max_valid_parking", 20.0)
            amb_nan = getattr(self, "ambiguous_parking_as_nan", True)
            park_tuples = [
                extract_parking_info(v, max_valid_spaces=max_park, ambiguous_as_nan=amb_nan)
                for v in park_s
            ]
            out["parking_spaces"] = [t[0] for t in park_tuples]
            out["has_parking"] = [t[1] for t in park_tuples]
            out["parking_count_ambiguous"] = [t[2] for t in park_tuples]
        else:
            out["parking_spaces"] = 0.0
            out["has_parking"] = 0
            out["parking_count_ambiguous"] = 0

        # 5. Floor information
        floor_s = self._get_col(X, "Floor", "floor")
        fnum_s = self._get_col(X, "floor_num")
        totf_s = self._get_col(X, "total_floors")
        if floor_s is not None and (fnum_s is None or totf_s is None):
            floor_tuples = [extract_floor_info(v) for v in floor_s]
            out["floor_num"] = [t[0] for t in floor_tuples]
            out["total_floors"] = [t[1] for t in floor_tuples]
        else:
            out["floor_num"] = pd.to_numeric(fnum_s, errors="coerce") if fnum_s is not None else np.nan
            out["total_floors"] = pd.to_numeric(totf_s, errors="coerce") if totf_s is not None else np.nan

        # 6. Categorical features with consistent string casting and unknown handling
        sub_s = self._get_col(X, "sub_area", "locality")
        title_s = self._get_col(X, "Title", "title")
        society_s = self._get_col(X, "Society", "society")

        for cat_col in CATEGORICAL_FEATURE_COLS:
            if cat_col == "sub_area":
                if sub_s is not None:
                    out["sub_area"] = (
                        sub_s.fillna("Unspecified")
                        .astype(str)
                        .str.strip()
                        .replace("", "Unspecified")
                        .str.title()
                    )
                elif title_s is not None:
                    soc_list = society_s if society_s is not None else [None] * len(title_s)
                    out["sub_area"] = [
                        extract_sub_area_from_title(t, s)
                        for t, s in zip(title_s, soc_list)
                    ]
                else:
                    out["sub_area"] = "Unspecified"
            else:
                cat_s = self._get_col(X, cat_col)
                if cat_s is not None:
                    out[cat_col] = (
                        cat_s.fillna("Unspecified")
                        .astype(str)
                        .str.strip()
                        .replace("", "Unspecified")
                    )
                else:
                    out[cat_col] = "Unspecified"

        return out[ALL_MODEL_FEATURE_COLS]


def build_preprocessor(scale_numeric: bool = True) -> ColumnTransformer:
    """
    Builds a scikit-learn ColumnTransformer for the extracted feature columns.
    Handles missing values via median/constant imputation and encodes categoricals.
    """
    if scale_numeric:
        num_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
    else:
        num_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
        ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unspecified")),
        ("encoder", OneHotEncoder(min_frequency=10, handle_unknown="ignore", sparse_output=False)),
    ])

    return ColumnTransformer(
        transformers=[
            ("num", num_pipeline, NUMERIC_FEATURE_COLS),
            ("cat", cat_pipeline, CATEGORICAL_FEATURE_COLS),
        ],
        remainder="drop",
    )
