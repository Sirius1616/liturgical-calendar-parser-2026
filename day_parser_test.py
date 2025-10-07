import re
import csv
from pathlib import Path
from datetime import datetime, timedelta
import calendar
import pdfplumber

PDF_FILE = "USCCB_2026_Feast_Calendar_CLEAN.pdf"
OUTPUT_CSV = "DAY_DATA.csv"
YEAR = 2026

# Liturgical colors
COLORS = ["Green", "White", "Violet", "Red", "Rose"]

# Map month names
MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}

# Set holy days of obligation (per PDF notes)
HDO_2026 = [
    # Example: Aug 15 not obligatory
    # Add other dates from PDF notes if required
    "2026-01-01",  # Solemnity of Mary, Mother of God (example)
]

output_rows = []

# Helper: determine first Friday/Saturday
def is_first_friday(date_obj):
    return date_obj.weekday() == 4 and date_obj.day <= 7

def is_first_saturday(date_obj):
    return date_obj.weekday() == 5 and date_obj.day <= 7

# Helper: parse feast rank
def parse_feast_rank(text):
    for rank in ["Solemnity", "Feast", "Memorial", "Optional Memorial", "Weekday", "Sunday"]:
        if rank.lower() in text.lower():
            return rank
    return ""

# Helper: extract liturgical color
def extract_color(text):
    pattern = r"(Green|White|Violet|Red|Rose)(\s*/\s*(Green|White|Violet|Red|Rose))?"
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        color = m.group(0).title().replace(" ", "")
        return color
    return ""

# Open PDF
with pdfplumber.open(PDF_FILE) as pdf:
    current_month = None
    week_row_counter = {}
    for page_num, page in enumerate(pdf.pages[12:], start=13):  # pages start at 13
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
                    week_row_counter[current_month] = 1
                    break

            if current_month is None:
                continue  # skip until we detect month

            # Detect date line
            m = re.match(r"^(\d{1,2})\s+(\w{3})\s+(.*)$", line)
            if not m:
                continue
            day_num, weekday_str, feast_text = m.groups()
            day_num = int(day_num)

            # Extract liturgical color
            color = extract_color(feast_text)
            # Remove color from feast text
            if color:
                feast_text_clean = re.sub(re.escape(color), "", feast_text, flags=re.IGNORECASE).strip()
            else:
                feast_text_clean = feast_text

            # Feast rank
            rank = parse_feast_rank(feast_text_clean)

            # Build date
            date_obj = datetime(YEAR, current_month, day_num)
            date_str = date_obj.strftime("%Y-%m-%d")

            # Flags
            first_friday = 1 if is_first_friday(date_obj) else 0
            first_saturday = 1 if is_first_saturday(date_obj) else 0
            hdo_flag = 1 if date_str in HDO_2026 else 0

            # Determine weekday_col (1=Sunday)
            weekday_col = (date_obj.weekday() + 1) % 7 + 1

            # Assign week_row (simple counter)
            week_row = week_row_counter[current_month]
            if weekday_col == 7:  # Saturday, increment row for next week
                week_row_counter[current_month] += 1

            row = {
                "date": date_str,
                "feast_primary_name": feast_text_clean,
                "feast_rank": rank,
                "liturgical_color": color,
                "is_holy_day_of_obligation": hdo_flag,
                "us_holiday_name": "",  # fill from PDF if exists
                "is_first_friday": first_friday,
                "is_first_saturday": first_saturday,
                "week_row": week_row,
                "weekday_col": weekday_col,
                "display_date_number": day_num,
                "belongs_to_month": 1,
                "source_page": page_num,
            }
            output_rows.append(row)

# Write CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "date","feast_primary_name","feast_rank","liturgical_color",
        "is_holy_day_of_obligation","us_holiday_name",
        "is_first_friday","is_first_saturday","week_row","weekday_col",
        "display_date_number","belongs_to_month","source_page"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Completed: {len(output_rows)} rows written to {OUTPUT_CSV}")
