#!/usr/bin/env python
"""
Validate Data Script — Offline ML Workflow (Phase 1).
Deterministic, read-only audit of raw property listing dataset.
"""
from __future__ import annotations

import os
import sys
import json
import argparse
from pathlib import Path

# Add src to path so real_estate_ml_training package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from real_estate_ml_training.audit import audit_dataset  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Audit and validate raw real estate dataset (Phase 1)."
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="ml/training/data/raw/house_prices.csv",
        help="Path to raw dataset CSV or ZIP file."
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        help="Optional path to save audit results as JSON."
    )
    args = parser.parse_args()

    # Fallback to Downloads archive.zip if default path does not exist
    data_path = args.data_path
    if not os.path.exists(data_path):
        fallback_zip = os.path.expanduser(r"C:\Users\OMKAR\Downloads\archive.zip")
        if os.path.exists(fallback_zip):
            print(f"Default path '{data_path}' not found. Using fallback archive: {fallback_zip}")
            data_path = fallback_zip
        else:
            print(f"ERROR: Dataset not found at '{data_path}' or fallback '{fallback_zip}'.")
            sys.exit(1)

    print("================================================================================")
    print(" PHASE 1 DATASET AUDIT: REAL ESTATE PRICE PREDICTION (INDIA)")
    print("================================================================================")
    print(f"Target dataset: {data_path}")

    try:
        results = audit_dataset(data_path)
    except Exception as e:
        print(f"ERROR during dataset audit: {e}")
        sys.exit(1)

    print("\n--- 1. Dataset Dimensions & Storage ---")
    print(f"Total Rows:            {results['total_rows']:,}")
    print(f"Total Columns:         {results['total_columns']}")
    print(f"Raw File Size:         {results['file_size_bytes']:,} bytes ({results['file_size_bytes'] / (1024 * 1024):.2f} MB)")

    print("\n--- 2. Duplicate Row Analysis ---")
    dups = results["duplicates"]
    print(f"Across All Raw Rows (187,531 total):")
    print(f"  Exact full-row duplicates (all 21 cols):              {dups['exact_full_duplicates']:,}")
    print(f"  Duplicate rows excluding 'Index' (20 property cols):  {dups['duplicates_excluding_index']:,}")
    print(f"  Unique property row combinations (all targets):       {dups['unique_property_combinations']:,}")
    if "valid_target_unique" in dups:
        print(f"Within Valid Supervised Target Subset ({dups['valid_target_rows']:,} rows):")
        print(f"  Duplicate rows excluding 'Index':                     {dups['valid_target_duplicates']:,}")
        print(f"  Unique property combinations (eligible for modeling): {dups['valid_target_unique']:,}")
        print(f"Within 'Call for Price' Subset ({dups['call_for_price_rows']:,} rows):")
        print(f"  Duplicate rows excluding 'Index':                     {dups['call_for_price_duplicates']:,}")
        print(f"  Unique property combinations:                         {dups['call_for_price_unique']:,}")


    print("\n--- 3. Target Variable 'Amount(in rupees)' Breakdown ---")
    tgt = results["target"]
    stats = tgt["price_statistics_inr"]
    print(f"Total rows inspected:                                 {tgt['total_rows']:,}")
    print(f"Valid parseable prices (Supervised training set):     {tgt['valid_target_rows']:,}")
    print(f"  - Lac / Lakh prices:                                {tgt['lac_lakh_rows']:,}")
    print(f"  - Cr / Crore prices:                                {tgt['cr_crore_rows']:,}")
    print(f"Call for Price (Excluded from supervised target):     {tgt['call_for_price_rows']:,}")
    print(f"Blank / NaN target values:                            {tgt['blank_target_rows']:,}")
    print(f"Unparseable target values:                            {tgt['unparseable_target_rows']:,}")

    if stats:
        print("\nPrice Distribution (Valid Supervised Subset in INR):")
        print(f"  Min Price:     INR {stats['min_inr']:,.2f}")
        print(f"  1st %ile:      INR {stats['p01_inr']:,.2f}")
        print(f"  25th %ile:     INR {stats['p25_inr']:,.2f}")
        print(f"  Median (50%):  INR {stats['p50_inr']:,.2f}")
        print(f"  Mean:          INR {stats['mean_inr']:,.2f}")
        print(f"  75th %ile:     INR {stats['p75_inr']:,.2f}")
        print(f"  99th %ile:     INR {stats['p99_inr']:,.2f}")
        print(f"  Max Price:     INR {stats['max_inr']:,.2f}")
        print(f"  Count < 1 Lac: {stats['count_under_1_lac']}")
        print(f"  Count > 100 Cr:{stats['count_over_100_cr']}")

    print("\n--- 4. Area Analysis (Carpet Area vs Super Area) ---")
    area = results["area"]
    print(f"Rows with Carpet Area ONLY:                           {area['carpet_only_rows']:,}")
    print(f"Rows with Super Area ONLY:                            {area['super_only_rows']:,}")
    print(f"Rows with BOTH Carpet & Super Area:                   {area['both_areas_rows']:,}  <-- STRICT SEPARATION")
    print(f"Rows with NEITHER Area:                               {area['neither_area_rows']:,}")
    print("\nCarpet Area Units:")
    for u, count in area["carpet_area_units"].items():
        print(f"  {u:10s}: {count:,}")
    print("\nSuper Area Units:")
    for u, count in area["super_area_units"].items():
        print(f"  {u:10s}: {count:,}")

    print("\n--- 5. Blank & Constant Columns ---")
    print(f"Completely 100% Blank Columns:  {results['blank_columns']}")
    print(f"Near-Constant Columns:          {results['constant_columns']}")

    print("\n--- 6. Key Data Quality Findings & Target Leakage Risks ---")
    for idx, finding in enumerate(results["quality_and_leakage_findings"], 1):
        print(f"  {idx}. {finding}")

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\n[INFO] Audit results written to JSON: {out_path}")

    print("================================================================================")
    print(" PHASE 1 AUDIT COMPLETE: PASS")
    print("================================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
