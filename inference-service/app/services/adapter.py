import math
from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd

from app.schemas.predict import PropertyPredictionRequest, AreaBasisEnum


class RequestAdapter:
    """
    Adapter converting validated PropertyPredictionRequest into a single-row
    pandas DataFrame consumable by the trained scikit-learn pipeline.
    """

    @staticmethod
    def normalize_category(
        val: Optional[str],
        col_name: str,
        allowed_categories: Dict[str, Any],
        raw_map: Dict[str, Dict[str, str]],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Normalizes a categorical value against the pipeline's learned categories.
        Returns (canonical_string, error_message).
        If val is None or empty, returns (None, None).
        """
        if val is None:
            return None, None
        s = val.strip()
        if not s:
            return None, None

        norm_key = " ".join(s.lower().replace("_", " ").replace("-", " ").split())
        col_allowed = allowed_categories.get(col_name)
        if col_allowed and norm_key not in col_allowed:
            return None, f"Value '{val}' is not a recognized category for '{col_name}'."

        col_raw = raw_map.get(col_name, {})
        canonical = col_raw.get(norm_key, s)
        return canonical, None

    @classmethod
    def request_to_dataframe(
        cls,
        request: PropertyPredictionRequest,
        allowed_categories: Dict[str, Any],
        raw_map: Dict[str, Dict[str, str]],
    ) -> pd.DataFrame:
        """
        Maps PropertyPredictionRequest to a 1-row DataFrame for PropertyFeatureExtractor.
        Adheres strictly to Phase 2 Treatment B parking semantics, area basis mapping,
        and learned categorical sets.
        """
        # 1. Location check and canonicalization
        loc_s = " ".join(request.location.strip().lower().split())
        allowed_locations = allowed_categories.get("location")
        if allowed_locations and loc_s not in allowed_locations:
            raise ValueError(f"UNSUPPORTED_LOCATION: Location '{request.location}' is not supported.")

        loc_raw_map = raw_map.get("location", {})
        canonical_location = loc_raw_map.get(loc_s, loc_s)

        # 2. Area mapping: carpet vs super (mutually exclusive from single input area_value in sqft)
        if request.area_basis == AreaBasisEnum.CARPET:
            carpet_sqft = float(request.area_value)
            has_carpet = 1
            carpet_verified = 1
            super_sqft = np.nan
            has_super = 0
            super_verified = 0
        else:
            carpet_sqft = np.nan
            has_carpet = 0
            carpet_verified = 0
            super_sqft = float(request.area_value)
            has_super = 1
            super_verified = 1

        # 3. BHK count
        bhk_val = float(request.bhk) if request.bhk is not None else np.nan

        # 4. Bathrooms & Balconies (preserves portal > 10 interval semantics as trained)
        if request.bathrooms is not None:
            bath_val = "> 10" if request.bathrooms > 10 else float(request.bathrooms)
        else:
            bath_val = np.nan

        if request.balcony is not None:
            balc_val = "> 10" if request.balcony > 10 else float(request.balcony)
        else:
            balc_val = np.nan

        # 5. Parking string under Phase 2 Treatment B semantics
        # The pipeline's extract_parking_info expects a string:
        # None/0 -> 'None' -> (0.0, 0, 0)
        # count <= 20 -> 'N Covered' -> (N.0, 1, 0)
        # count > 20 -> 'N Covered' -> (NaN, 1, 1) [Treatment B semantic-unknown]
        if request.parking_spaces is None or request.parking_spaces == 0:
            parking_str = "None"
        else:
            parking_str = f"{int(request.parking_spaces)} Covered"

        # 6. Floors
        floor_num_val = float(request.floor_number) if request.floor_number is not None else np.nan
        total_floors_val = float(request.total_floors) if request.total_floors is not None else np.nan

        # 7. Categorical fields
        furnishing_canon, err = cls.normalize_category(
            request.furnishing, "Furnishing", allowed_categories, raw_map
        )
        if err:
            raise ValueError(f"INVALID_CATEGORY: {err}")

        transaction_canon, err = cls.normalize_category(
            request.transaction_type, "Transaction", allowed_categories, raw_map
        )
        if err:
            raise ValueError(f"INVALID_CATEGORY: {err}")

        status_canon, err = cls.normalize_category(
            request.status, "Status", allowed_categories, raw_map
        )
        if err:
            raise ValueError(f"INVALID_CATEGORY: {err}")

        facing_canon, err = cls.normalize_category(
            request.facing, "facing", allowed_categories, raw_map
        )
        if err:
            raise ValueError(f"INVALID_CATEGORY: {err}")

        ownership_canon, err = cls.normalize_category(
            request.ownership, "Ownership", allowed_categories, raw_map
        )
        if err:
            raise ValueError(f"INVALID_CATEGORY: {err}")

        row_dict = {
            "carpet_area_sqft": carpet_sqft,
            "has_carpet_area": has_carpet,
            "carpet_area_unit_verified": carpet_verified,
            "super_area_sqft": super_sqft,
            "has_super_area": has_super,
            "super_area_unit_verified": super_verified,
            "bhk": bhk_val,
            "Bathroom": bath_val,
            "Balcony": balc_val,
            "Car Parking": parking_str,
            "floor_num": floor_num_val,
            "total_floors": total_floors_val,
            "location": canonical_location,
            "Furnishing": furnishing_canon if furnishing_canon is not None else "Unspecified",
            "Transaction": transaction_canon if transaction_canon is not None else "Unspecified",
            "Status": status_canon if status_canon is not None else "Unspecified",
            "facing": facing_canon if facing_canon is not None else "Unspecified",
            "Ownership": ownership_canon if ownership_canon is not None else "Unspecified",
        }

        return pd.DataFrame([row_dict])
