import math
import numpy as np
import pytest
from app.schemas.predict import PropertyPredictionRequest, AreaBasisEnum
from app.services.adapter import RequestAdapter


@pytest.fixture
def dummy_categories():
    return {
        "location": {"thane", "whitefield", "andheri west"},
        "Furnishing": {"furnished", "semi furnished", "unfurnished", "unspecified"},
        "Transaction": {"resale", "new property", "unspecified"},
        "Status": {"ready to move", "unspecified"},
        "facing": {"east", "north", "north east", "unspecified"},
        "Ownership": {"freehold", "co operative society", "leasehold", "unspecified"},
    }


@pytest.fixture
def dummy_raw_map():
    return {
        "location": {"thane": "thane", "whitefield": "whitefield", "andheri west": "andheri west"},
        "Furnishing": {"furnished": "Furnished", "semi furnished": "Semi-Furnished", "unfurnished": "Unfurnished", "unspecified": "Unspecified"},
        "Transaction": {"resale": "Resale", "new property": "New Property", "unspecified": "Unspecified"},
        "Status": {"ready to move": "Ready to Move", "unspecified": "Unspecified"},
        "facing": {"east": "East", "north": "North", "north east": "North - East", "unspecified": "Unspecified"},
        "Ownership": {"freehold": "Freehold", "co operative society": "Co-operative Society", "leasehold": "Leasehold", "unspecified": "Unspecified"},
    }


def test_adapter_carpet_area_mapping(dummy_categories, dummy_raw_map):
    req = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        area_value=1250.0,
        area_basis=AreaBasisEnum.CARPET,
    )
    df = RequestAdapter.request_to_dataframe(req, dummy_categories, dummy_raw_map)
    assert len(df) == 1
    assert df.loc[0, "carpet_area_sqft"] == 1250.0
    assert np.isnan(df.loc[0, "super_area_sqft"])
    assert df.loc[0, "location"] == "thane"


def test_adapter_super_area_mapping(dummy_categories, dummy_raw_map):
    req = PropertyPredictionRequest(
        schema_version="1.0",
        location="Whitefield",
        area_value=1500.0,
        area_basis=AreaBasisEnum.SUPER,
    )
    df = RequestAdapter.request_to_dataframe(req, dummy_categories, dummy_raw_map)
    assert len(df) == 1
    assert np.isnan(df.loc[0, "carpet_area_sqft"])
    assert df.loc[0, "super_area_sqft"] == 1500.0
    assert df.loc[0, "location"] == "whitefield"


def test_adapter_parking_treatment_b_semantics(dummy_categories, dummy_raw_map):
    # Case 1: None / missing parking
    req_none = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        area_value=1000.0,
        area_basis=AreaBasisEnum.CARPET,
        parking_spaces=None,
    )
    df_none = RequestAdapter.request_to_dataframe(req_none, dummy_categories, dummy_raw_map)
    assert df_none.loc[0, "Car Parking"] == "None"

    # Case 2: 0 parking spaces
    req_zero = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        area_value=1000.0,
        area_basis=AreaBasisEnum.CARPET,
        parking_spaces=0,
    )
    df_zero = RequestAdapter.request_to_dataframe(req_zero, dummy_categories, dummy_raw_map)
    assert df_zero.loc[0, "Car Parking"] == "None"

    # Case 3: Typical valid count <= 20
    req_two = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        area_value=1000.0,
        area_basis=AreaBasisEnum.CARPET,
        parking_spaces=2,
    )
    df_two = RequestAdapter.request_to_dataframe(req_two, dummy_categories, dummy_raw_map)
    assert df_two.loc[0, "Car Parking"] == "2 Covered"

    # Case 4: Ambiguous slot number > 20 (Treatment B)
    req_amb = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        area_value=1000.0,
        area_basis=AreaBasisEnum.CARPET,
        parking_spaces=42,
    )
    df_amb = RequestAdapter.request_to_dataframe(req_amb, dummy_categories, dummy_raw_map)
    assert df_amb.loc[0, "Car Parking"] == "42 Covered"


def test_adapter_floor_mapping(dummy_categories, dummy_raw_map):
    req = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        area_value=1000.0,
        area_basis=AreaBasisEnum.CARPET,
        floor_number=0.0,
        total_floors=4.0,
    )
    df = RequestAdapter.request_to_dataframe(req, dummy_categories, dummy_raw_map)
    assert df.loc[0, "floor_num"] == 0.0
    assert df.loc[0, "total_floors"] == 4.0


def test_adapter_categorical_normalization(dummy_categories, dummy_raw_map):
    req = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        area_value=1000.0,
        area_basis=AreaBasisEnum.CARPET,
        furnishing="SEMI_FURNISHED",
        transaction_type="new-property",
        facing="North - East",
        ownership="Co-operative Society",
    )
    df = RequestAdapter.request_to_dataframe(req, dummy_categories, dummy_raw_map)
    assert df.loc[0, "Furnishing"] == "Semi-Furnished"
    assert df.loc[0, "Transaction"] == "New Property"
    assert df.loc[0, "facing"] == "North - East"
    assert df.loc[0, "Ownership"] == "Co-operative Society"


def test_adapter_unsupported_location_raises(dummy_categories, dummy_raw_map):
    req = PropertyPredictionRequest(
        schema_version="1.0",
        location="Atlantis",
        area_value=1000.0,
        area_basis=AreaBasisEnum.CARPET,
    )
    with pytest.raises(ValueError, match="UNSUPPORTED_LOCATION"):
        RequestAdapter.request_to_dataframe(req, dummy_categories, dummy_raw_map)


def test_adapter_invalid_category_raises(dummy_categories, dummy_raw_map):
    req = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        area_value=1000.0,
        area_basis=AreaBasisEnum.CARPET,
        furnishing="Ultra Luxurious Golden Furnished",
    )
    with pytest.raises(ValueError, match="INVALID_CATEGORY"):
        RequestAdapter.request_to_dataframe(req, dummy_categories, dummy_raw_map)


def test_adapter_bathroom_interval_gt_10(dummy_categories, dummy_raw_map):
    req = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        area_value=1000.0,
        area_basis=AreaBasisEnum.CARPET,
        bathrooms=12.0,
        balcony=2,
    )
    df = RequestAdapter.request_to_dataframe(req, dummy_categories, dummy_raw_map)
    assert df.loc[0, "Bathroom"] == "> 10"
    assert df.loc[0, "Balcony"] == 2.0


def test_adapter_extracts_exact_23_features_in_order(dummy_categories, dummy_raw_map):
    from real_estate_ml_training.features import PropertyFeatureExtractor, ALL_MODEL_FEATURE_COLS

    req = PropertyPredictionRequest(
        schema_version="1.0",
        location="Thane",
        sub_area="Kothrud",
        area_value=1200.0,
        area_basis=AreaBasisEnum.CARPET,
        bhk=2,
        bathrooms=2.0,
        balcony=1,
        parking_spaces=2,
        floor_number=2.0,
        total_floors=5.0,
        furnishing="Semi-Furnished",
        transaction_type="Resale",
        status="Ready to Move",
        facing="East",
        ownership="Freehold",
    )
    df = RequestAdapter.request_to_dataframe(req, dummy_categories, dummy_raw_map)
    ext = PropertyFeatureExtractor()
    out = ext.transform(df)

    # 1. Exact 23-feature column order
    assert list(out.columns) == ALL_MODEL_FEATURE_COLS
    assert len(out.columns) == 23

    # 2. Key feature checks
    row = out.iloc[0]
    assert row["carpet_area_sqft"] == 1200.0
    assert row["has_carpet_area"] == 1
    assert row["carpet_area_unit_verified"] == 1
    assert np.isnan(row["super_area_sqft"])
    assert row["has_super_area"] == 0
    assert row["super_area_unit_verified"] == 0
    assert row["bhk"] == 2.0
    assert row["bathroom"] == 2.0
    assert row["bathroom_is_gt_10"] == 0
    assert row["balcony"] == 1.0
    assert row["balcony_is_gt_10"] == 0
    assert row["parking_spaces"] == 2.0
    assert row["has_parking"] == 1
    assert row["parking_count_ambiguous"] == 0
    assert row["floor_num"] == 2.0
    assert row["total_floors"] == 5.0
    assert row["location"] == "thane"
    assert row["Furnishing"] == "Semi-Furnished"
    assert row["Transaction"] == "Resale"
    assert row["Status"] == "Ready to Move"
    assert row["facing"] == "East"
    assert row["Ownership"] == "Freehold"
