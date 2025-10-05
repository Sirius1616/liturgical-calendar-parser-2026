#!/usr/bin/env python
# src/build_datasets.py

import os
import argparse
import pandas as pd
from .parse_pdf import extract_calendar_data
from .utils import ensure_dir, create_date_skeleton, compute_week_row_for_month, normalize_color


def week_label(row: pd.Series) -> str:
    """
    Generate a human-friendly label for a week range.
    Example: "Week of Jan 5–11"
    """
    s = pd.to_datetime(row['WeekStart'])
    e = pd.to_datetime(row['WeekEnd'])
    return f"Week of {s.strftime('%b')} {s.day}–{e.day}"


def build_all(input_pdf: str, out_dir: str) -> None:
    """
    Orchestrates building all datasets from the liturgical calendar PDF.
    
    Args:
        input_pdf (str): Path to the input PDF file.
        out_dir (str): Directory to save generated datasets.
    """
    ensure_dir(out_dir)

    print(f"[INFO] Extracting raw data from: {input_pdf}")
    raw = extract_calendar_data(input_pdf)

    # Save raw dataset
    raw_csv = os.path.join(out_dir, "raw_calendar.csv")
    raw.to_csv(raw_csv, index=False)
    print(f"[INFO] Raw dataset saved → {raw_csv}")

    # === Example post-processing ===
    # Group by weeks (assuming WeekStart/WeekEnd columns exist in raw DataFrame)
    if "WeekStart" in raw.columns and "WeekEnd" in raw.columns:
        print("[INFO] Building weekly index dataset...")

        widx = (
            raw.groupby(["WeekStart", "WeekEnd"])
            .size()
            .reset_index(name="NumEntries")
        )

        # Add human-friendly week labels
        widx["WeekLabel"] = widx.apply(week_label, axis=1)

        widx_csv = os.path.join(out_dir, "weekly_index.csv")
        widx.to_csv(widx_csv, index=False)
        print(f"[INFO] Weekly index dataset saved → {widx_csv}")
    else:
        print("[WARN] Skipping weekly index dataset (WeekStart/WeekEnd not found)")

    print("[SUCCESS] All datasets built.")


def main():
    parser = argparse.ArgumentParser(description="Build datasets from liturgical calendar PDF")
    parser.add_argument("input", help="Path to input PDF file")
    parser.add_argument("--out", default="output", help="Output directory for datasets")
    args = parser.parse_args()

    build_all(args.input, args.out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build 2026 liturgical calendar CSV datasets.')
    parser.add_argument('--input', type=str, default='input/USCCB_2026_Feast_Calendar_CLEAN.pdf',
                        help='Path to input PDF')
    parser.add_argument('--out', type=str, default='data/',
                        help='Output folder for CSVs')
    args = parser.parse_args()
    build_all(args.input, args.out)

