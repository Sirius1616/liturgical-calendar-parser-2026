#!/usr/bin/env python
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

def validate():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(REPORTS_DIR, "qc_report_2026.md")

    # Load daily calendar
    daily_path = os.path.join(DATA_DIR, "daily_calendar_2026.csv")
    df = pd.read_csv(daily_path)

    issues = []

    # Check date coverage
    if df["date"].duplicated().any():
        issues.append("❌ Duplicate dates found")
    else:
        issues.append("✅ No duplicate dates")

    if df.isnull().any().any():
        issues.append("❌ Missing values detected")
    else:
        issues.append("✅ No missing values")

    # Write report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# QC Report – 2026 Calendar\n\n")
        for line in issues:
            f.write(f"- {line}\n")

    print(f"✅ Validation complete. Report saved to {report_path}")

if __name__ == "__main__":
    validate()
