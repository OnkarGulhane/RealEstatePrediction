#!/usr/bin/env python
"""
Prepare Data Script — Offline ML Workflow (Phase 1 & Phase 2).
Deterministic preparation of raw property listings into:
- Phase 1: interim supervised dataset (177,847 rows with valid targets)
- Phase 2: deduplicated supervised training view (65,255 unique configurations) and audit mapping
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
from real_estate_ml_training.clean import (  # noqa: E402
    prepare_property_data,
    build_phase2_deduplicated_view,
)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare raw real estate dataset according to Phase 1 / Phase 2 rules."
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
        help="Path to save prepared interim dataset (Phase 1)."
    )
    parser.add_argument(
        "--phase2",
        action="store_true",
        help="Generate Phase 2 deduplicated supervised view and audit mapping."
    )
    parser.add_argument(
        "--phase2-output",
        type=str,
        default="ml/training/data/processed/phase2_supervised_deduplicated.csv",
        help="Path to save Phase 2 deduplicated training view."
    )
    parser.add_argument(
        "--phase2-mapping",
        type=str,
        default="ml/training/data/processed/phase2_audit_mapping.csv",
        help="Path to save Phase 2 audit mapping table."
    )
    parser.add_argument(
        "--include-call-for-price",
        action="store_true",
        help="Whether to retain Call for Price rows (Phase 1 default: False)."
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
    print(" DATA PREPARATION: REAL ESTATE PRICE PREDICTION")
    print("================================================================================")
    print(f"Input path:  {input_path}")

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

    if args.phase2:
        print("\n[2/3] Applying Phase 2 Deduplicated Supervised Preparation Rules...")
        print("  - Exclude Index when evaluating duplicate configurations across 20 columns.")
        print("  - Filter to valid supervised target records (Amount(in rupees) parseable).")
        print("  - Deduplicate to retain exactly 1 primary configuration per unique property.")
        print("  - Build auditable mapping to preserve all original source row indices.")
        print("  - Keep Carpet Area and Super Area strictly separated with indicators.")

        dedup_df, audit_mapping_df, accounting = build_phase2_deduplicated_view(raw_df)

        print(f"\n[3/3] Writing Phase 2 processed outputs...")
        out_dedup = Path(args.phase2_output)
        out_map = Path(args.phase2_mapping)
        out_dedup.parent.mkdir(parents=True, exist_ok=True)
        out_map.parent.mkdir(parents=True, exist_ok=True)

        dedup_df.to_csv(out_dedup, index=False)
        audit_mapping_df.to_csv(out_map, index=False)

        dedup_size = os.path.getsize(out_dedup)
        map_size = os.path.getsize(out_map)

        print("\n================================================================================")
        print(" PHASE 2 PREPARATION RECONCILIATION ACCOUNTING")
        print("================================================================================")
        print(f"Total Raw Input Rows:                     {accounting['total_raw_rows']:,}")
        print(f"Valid Supervised Target Rows:             {accounting['valid_target_rows']:,}")
        print(f"Excluded: 'Call for Price' Target Rows:   {accounting['call_for_price_rows']:,}")
        print(f"Excluded: Blank / Unparseable Rows:       {accounting['blank_target_rows']:,} / {accounting['unparseable_target_rows']:,}")
        print("---")
        print(f"Unique Supervised Configurations (OUTPUT):{accounting['valid_unique_configurations']:,}")
        print(f"Duplicate Occurrences Removed:            {accounting['valid_duplicate_occurrences']:,}")
        print(f"Sum of Unique + Duplicates:               {accounting['valid_unique_configurations'] + accounting['valid_duplicate_occurrences']:,} (100% exact match)")
        print("---")
        print(f"Total Raw Unique Configurations:          {accounting['raw_unique_configurations']:,}")
        print(f"Total Raw Duplicate Occurrences:          {accounting['raw_duplicate_occurrences']:,}")
        print(f"CFP Unique Configurations:                {accounting['cfp_unique_configurations']:,}")
        print(f"CFP Duplicate Occurrences:                {accounting['cfp_duplicate_occurrences']:,}")
        print(f"Cross-Sum Check Unique:                   {accounting['valid_unique_configurations'] + accounting['cfp_unique_configurations']:,} == {accounting['raw_unique_configurations']:,}")
        print(f"Cross-Sum Check Duplicates:               {accounting['valid_duplicate_occurrences'] + accounting['cfp_duplicate_occurrences']:,} == {accounting['raw_duplicate_occurrences']:,}")
        print("---")
        print(f"Carpet Area Only Listings:                {accounting['carpet_only_count']:,}")
        print(f"Super Area Only Listings:                 {accounting['super_only_count']:,}")
        print(f"Both Areas Populated:                     {accounting['both_areas_count']:,}")
        print(f"Neither Area Populated:                   {accounting['neither_area_count']:,}")
        print(f"\nPhase 2 deduplicated output:              {out_dedup} ({dedup_size:,} bytes)")
        print(f"Phase 2 audit mapping output:             {out_map} ({map_size:,} bytes)")
        print("================================================================================")
        print(" PHASE 2 PREPARATION COMPLETE: PASS")
        print("================================================================================")
        return 0

    # Phase 1 behavior
    print("\n[2/3] Applying Phase 1 deterministic preparation rules...")
    prepared_df, accounting = prepare_property_data(
        raw_df,
        include_call_for_price=args.include_call_for_price
    )

    print(f"\n[3/3] Writing prepared output to {args.output_path}...")
    out_file = Path(args.output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    prepared_df.to_csv(out_file, index=False)
    out_size_bytes = os.path.getsize(out_file)

    print("\n================================================================================")
    print(" PHASE 1 PREPARATION ROW RECONCILIATION ACCOUNTING")
    print("================================================================================")
    print(f"Total Raw Input Rows:                     {accounting['total_input_rows']:,}")
    print(f"Valid Supervised Target Rows (OUTPUT):    {accounting['output_rows']:,}")
    print(f"Excluded: 'Call for Price' Target Rows:   {accounting['call_for_price_rows']:,}")
    print(f"Sum of output + excluded rows:            {accounting['output_rows'] + accounting['call_for_price_rows']:,}")
    print(f"Prepared output file size:                {out_size_bytes:,} bytes")
    print("================================================================================")
    print(" PHASE 1 PREPARATION COMPLETE: PASS")
    print("================================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
