import re
import csv
from pathlib import Path
from datetime import datetime
import calendar
import pdfplumber

PDF_FILE = "USCCB_2026_Feast_Calendar_CLEAN.pdf"
OUTPUT_CSV = "data/daily_bible_citations_2026.csv"
YEAR = 2026

# Map month names
MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}

def extract_bible_citation(text):
    """Extract short Bible citation from a line"""
    # Simple pattern: book name + chapter:verse(s), optionally multiple ranges separated by ';'
    pattern = r"\b(?:[1-3]?\s?[A-Za-z]+)\s\d{1,3}:\d{1,3}(?:–\d{1,3})?(?:;\s?[1-3]?\s?[A-Za-z]+\s\d{1,3}:\d{1,3}(?:–\d{1,3})?)*"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return ""

def main():
    output_rows = []

    with pdfplumber.open(PDF_FILE) as pdf:
        current_month = None

        # Skip to the weekly pages (you can adjust page index if needed)
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            lines = text.split("\n")

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect month header
                for month_name, month_num in MONTHS.items():
                    if month_name in line.lower():
                        current_month = month_num
                        break
                if current_month is None:
                    continue

                # Detect date line: e.g., "1 Tue" or "12 Fri"
                m = re.match(r"^(\d{1,2})\s+\w{3}", line)
                if not m:
                    continue
                day_num = int(m.group(1))
                try:
                    date_obj = datetime(YEAR, current_month, day_num)
                except ValueError:
                    continue  # skip invalid dates

                # Extract Bible citation
                citation = extract_bible_citation(line)
                if citation:
                    row = {
                        "Date": date_obj.strftime("%Y-%m-%d"),
                        "BibleCitationShort": citation,
                        "SourceLine": line
                    }
                    output_rows.append(row)

    # Write CSV
    Path("data").mkdir(parents=True, exist_ok=True)
    fieldnames = ["Date", "BibleCitationShort", "SourceLine"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Completed: {len(output_rows)} rows written to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
