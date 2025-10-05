#!/usr/bin/env python
import os
import pandas as pd
from parse_pdf import extract_calendar_data

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def build_datasets():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Step 1: Extract raw data from PDF
    df = extract_calendar_data("input/calendar_2026.pdf")

    # Step 2: Export different CSVs
    df.to_csv(os.path.join(DATA_DIR, "daily_calendar_2026.csv"), index=False)

    highlighted = df[df["rank"].isin(["Solemnity", "Feast"])]
    highlighted.to_csv(os.path.join(DATA_DIR, "highlighted_events_2026.csv"), index=False)

    simple = df[["date", "feast", "color"]]
    simple.to_csv(os.path.join(DATA_DIR, "simplified_calendar_2026.csv"), index=False)

    # (Weekly index, readings, holidays would be added here)

    print("✅ CSV files generated in /data")

if __name__ == "__main__":
    build_datasets()
