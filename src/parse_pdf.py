#!/usr/bin/env python
import pandas as pd

def extract_calendar_data(pdf_path: str) -> pd.DataFrame:
    """
    Mock PDF parser for now.
    Replace this with real PyMuPDF logic to parse columns from the PDF.
    """
    data = {
        "date": ["2026-01-01", "2026-01-02"],
        "feast": ["Solemnity of Mary", "Saint Basil"],
        "rank": ["Solemnity", "Memorial"],
        "color": ["White", "White"],
        "notes": ["Holy Day of Obligation", ""],
    }
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = extract_calendar_data("input/calendar_2026.pdf")
    print(df.head())
