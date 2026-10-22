#!/usr/bin/env python
"""
Prepare Data Script — Offline ML Workflow (Phase 1).
Deterministic preparation of raw property listings into a supervised-training-ready interim dataset.
Never modifies raw data in place.
Outputs strictly to local gitignored paths.
"""
from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path

# Add src to path so real_estate_ml_training package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd
from real_estate_ml_training.clean import prepare_property_data  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Prepare raw real estate dataset according to Phase 1 rules."
    )
    parser.add_argument(
        "--input-path",
        type=str,
        default="ml/training/data/raw/house_prices.csv",
        help="Path to raw dataset CSV or ZIP file."
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="ml/training/data/interim/prepared_properties.csv",
        help="Path to save prepared interim dataset (must be in gitignored folder)."
    )
    parser.add_argument(
        "--include-call-for-price",
        action="store_true",
        help="Whether to retain Call for Price rows (default: False; excluded from supervised target)."
    )
    args = parser.parse_args()

    input_path = args.input_path
    if not os.path.exists(input_path):
        fallback_zip = os.path.expanduser(r"C:\Users\OMKAR\Downloads\archive.zip")
        if os.path.exists(fallback_zip):
            print(f"[INFO] Using fallback archive: {fallback_zip}")
            input_path = fallback_zip
        else:
            print(f"ERROR: Raw dataset not found at '{input_path}'.")
            sys.exit(1)

    print("================================================================================")
    print(" PHASE 1 DATA PREPARATION: REAL ESTATE PRICE PREDICTION")
    print("================================================================================")
    print(f"Input path:  {input_path}")
    print(f"Output path: {args.output_path}")

    # Load raw data read-only
    print("\n[1/3] Reading raw dataset (read-only)...")
    if input_path.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(input_path) as z:
            with z.open("house_prices.csv") as f:
                raw_df = pd.read_csv(f)
    else:
        raw_df = pd.read_csv(input_path)

    initial_row_count = len(raw_df)
    print(f"Loaded {initial_row_count:,} raw listing rows with {len(raw_df.columns)} columns.")

    # Execute deterministic preparation
    print("\n[2/3] Applying Phase 1 deterministic preparation rules...")
    print("  - Exclude Index from model-ready feature columns.")
    print("  - Drop completely blank columns (Dimensions, Plot Area).")
    print("  - Exclude target-leaking fields (Description, Price (in rupees)).")
    print("  - Parse Amount(in rupees) to numeric INR.")
    print("  - Separate Carpet Area and Super Area strictly (zero conflation).")
    print("  - Standardize verified area units (sqft, sqyrd, sqm); flag regional units.")
    print("  - Exclude 'Call for Price' from supervised target set.")

    prepared_df, accounting = prepare_property_data(
        raw_df,
        include_call_for_price=args.include_call_for_price
    )

    # Save prepared dataset to ignored directory
    print(f"\n[3/3] Writing prepared output to {args.output_path}...")
    out_file = Path(args.output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if str(out_file).endswith(".parquet"):
        prepared_df.to_parquet(out_file, index=False)
    else:
        prepared_df.to_csv(out_file, index=False)

    out_size_bytes = os.path.getsize(out_file)

    print("\n================================================================================")
    print(" PHASE 1 PREPARATION ROW RECONCILIATION ACCOUNTING")
    print("================================================================================")
    print(f"Total Raw Input Rows:                     {accounting['total_input_rows']:,}")
    print(f"Valid Supervised Target Rows (OUTPUT):    {accounting['output_rows']:,}")
    print(f"Excluded: 'Call for Price' Target Rows:   {accounting['call_for_price_rows']:,}")
    print(f"Excluded: Blank / NaN Target Rows:        {accounting['blank_target_rows']:,}")
    print(f"Excluded: Unparseable Target Rows:        {accounting['unparseable_target_rows']:,}")

    # Mathematical reconciliation verification
    reconciled_sum = (
        accounting["output_rows"]
        + accounting["call_for_price_rows"]
        + accounting["blank_target_rows"]
        + accounting["unparseable_target_rows"]
    )
    print(f"Sum of output + excluded rows:            {reconciled_sum:,}")
    if reconciled_sum == accounting["total_input_rows"]:
        print("Reconciliation Status:                    100% EXACT MATCH (0 unaccounted rows)")
    else:
        print(f"Reconciliation Status:                    MISMATCH! Discrepancy: {accounting['total_input_rows'] - reconciled_sum}")
        sys.exit(1)

    print("\nArea Accounting in Prepared Dataset:")
    print(f"  Rows with Carpet Area:                  {accounting['carpet_area_count']:,}")
    print(f"  Rows with Super Area:                   {accounting['super_area_count']:,}")
    print(f"  Rows with BOTH Carpet & Super Area:     {accounting['both_areas_count']:,} (Preserved strict separation)")
    print(f"  Rows with NEITHER Area:                 {accounting['neither_area_count']:,}")
    print(f"\nPrepared output file size:               {out_size_bytes:,} bytes ({out_size_bytes / (1024 * 1024):.2f} MB)")
    print(f"Prepared output columns ({len(prepared_df.columns)}):           {prepared_df.columns.tolist()}")
    print("================================================================================")
    print(" PHASE 1 PREPARATION COMPLETE: PASS")
    print("================================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
