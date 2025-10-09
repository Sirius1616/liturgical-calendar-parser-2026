
import re
import csv
import argparse
import calendar
import subprocess
import pdfplumber
from pathlib import Path
from datetime import datetime, timedelta
from utils.parsers import (is_first_friday, is_first_saturday,
                            parse_feast_rank, extract_color,
                            extract_bible_citation
                            )

# ----------------------------
# DAY_DATA parser
# ----------------------------
def parse_day_data(pdf_file, year, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "DAY_DATA.csv"

    MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
    HDO_2026 = ["2026-01-01"]  # Example, extend as per PDF

    output_rows = []

    with pdfplumber.open(pdf_file) as pdf:
        current_month = None
        week_row_counter = {}

        for page_num, page in enumerate(pdf.pages[12:], start=13):  # start at page 13
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
                    continue

                # Detect date line
                m = re.match(r"^(\d{1,2})\s+(\w{3})\s+(.*)$", line)
                if not m:
                    continue
                day_num, weekday_str, feast_text = m.groups()
                day_num = int(day_num)

                color = extract_color(feast_text)
                feast_text_clean = re.sub(re.escape(color), "", feast_text, flags=re.IGNORECASE).strip() if color else feast_text
                rank = parse_feast_rank(feast_text_clean)
                date_obj = datetime(year, current_month, day_num)
                date_str = date_obj.strftime("%Y-%m-%d")

                first_friday = 1 if is_first_friday(date_obj) else 0
                first_saturday = 1 if is_first_saturday(date_obj) else 0
                hdo_flag = 1 if date_str in HDO_2026 else 0

                weekday_col = (date_obj.weekday() + 1) % 7 + 1
                week_row = week_row_counter[current_month]
                if weekday_col == 7:
                    week_row_counter[current_month] += 1

                row = {
                    "date": date_str,
                    "feast_primary_name": feast_text_clean,
                    "feast_rank": rank,
                    "liturgical_color": color,
                    "is_holy_day_of_obligation": hdo_flag,
                    "us_holiday_name": "",
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
    fieldnames = [
        "date","feast_primary_name","feast_rank","liturgical_color",
        "is_holy_day_of_obligation","us_holiday_name",
        "is_first_friday","is_first_saturday","week_row","weekday_col",
        "display_date_number","belongs_to_month","source_page"
    ]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Completed: {len(output_rows)} rows written to {output_csv}")
    return output_rows  # return rows for further processing

# ----------------------------
# Year-at-a-Glance
# ----------------------------
def generate_year_at_a_glance(day_rows, out_dir):
    """Generate liturgical_calendar_2026_simple.csv from DAY_DATA"""
    out_dir = Path(out_dir)
    output_csv = out_dir / "liturgical_calendar_2026_simple.csv"

    # Sort by date
    day_rows_sorted = sorted(day_rows, key=lambda x: x["date"])
    simple_rows = []

    for row in day_rows_sorted:
        simple_row = {
            "Date": row["date"],
            "DayOfMonth": row["display_date_number"],
            "DayOfWeek": datetime.strptime(row["date"], "%Y-%m-%d").strftime("%a"),
            "LiturgicalColor": row["liturgical_color"]
        }
        simple_rows.append(simple_row)

    fieldnames = ["Date", "DayOfMonth", "DayOfWeek", "LiturgicalColor"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(simple_rows)

    print(f"Completed: {len(simple_rows)} rows written to {output_csv}")

# ----------------------------
# Weekly index
# ----------------------------
def generate_weekly_index(day_rows, out_dir):
    """
    day_rows: list of dicts from DAY_DATA.csv (already parsed)
    out_dir: folder to write weekly_index_2026.csv
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "weekly_index_2026.csv"

    # Define liturgical seasons (start and end dates)
    SEASONS = [
        ("Advent", datetime(2025, 11, 30), datetime(2025, 12, 24)),
        ("Christmas", datetime(2025, 12, 25), datetime(2026, 1, 5)),
        ("Ordinary Time", datetime(2026, 1, 6), datetime(2026, 2, 16)),  # up to Ash Wednesday
        ("Lent", datetime(2026, 2, 17), datetime(2026, 4, 4)),  # Ash Wed → Holy Saturday
        ("Easter", datetime(2026, 4, 5), datetime(2026, 5, 23)),  # Easter Sunday → Pentecost
        ("Ordinary Time", datetime(2026, 5, 24), datetime(2026, 11, 28)),  # after Pentecost → Advent
        ("Advent", datetime(2026, 11, 29), datetime(2026, 12, 24)),
    ]

    # Sort day_rows by date
    day_rows_sorted = sorted(day_rows, key=lambda r: datetime.strptime(r["date"], "%Y-%m-%d"))

    # Prepare weekly index
    weekly_index = []
    season_week_counters = {}  # count weeks per season
    seen_weeks = set()

    for row in day_rows_sorted:
        date_obj = datetime.strptime(row["date"], "%Y-%m-%d")
        # Calculate week start (Monday) and week end (Sunday)
        week_start = date_obj - timedelta(days=date_obj.weekday())  # Monday
        week_end = week_start + timedelta(days=6)

        # Skip duplicate weeks
        week_key = week_start.strftime("%Y-%m-%d")
        if week_key in seen_weeks:
            continue
        seen_weeks.add(week_key)

        # Determine season
        season_name = "Ordinary Time"
        for season, start, end in SEASONS:
            if start <= date_obj <= end:
                season_name = season
                break

        # Increment week count per season for liturgical week label
        if season_name not in season_week_counters:
            season_week_counters[season_name] = 1
        else:
            season_week_counters[season_name] += 1
        liturgical_week_label = f"{season_week_counters[season_name]}{'st' if season_week_counters[season_name]==1 else 'nd' if season_week_counters[season_name]==2 else 'rd' if season_week_counters[season_name]==3 else 'th'} Week of {season_name}"

        week_label = f"Week of {week_start.strftime('%b')} {week_start.day}–{week_end.day}"

        weekly_index.append({
            "WeekStart": week_start.strftime("%Y-%m-%d"),
            "WeekEnd": week_end.strftime("%Y-%m-%d"),
            "WeekLabel": week_label,
            "LiturgicalWeekLabel": liturgical_week_label,
            "Season": season_name,
            "MonthForMiniCal": week_start.strftime("%Y-%m"),
            "WeekNumberInYear": week_start.isocalendar()[1]
        })

    # Write CSV
    fieldnames = ["WeekStart", "WeekEnd", "WeekLabel", "LiturgicalWeekLabel", "Season", "MonthForMiniCal", "WeekNumberInYear"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(weekly_index)

    print(f"Completed: {len(weekly_index)} rows written to {output_csv}")



# ----------------------------
# Bible Citations Extraction
# ----------------------------
def extract_bible_citation(text):
    """Extract short Bible citation from a line"""
    pattern = r"\b(?:[1-3]?\s?[A-Za-z]+)\s\d{1,3}:\d{1,3}(?:–\d{1,3})?(?:;\s?[1-3]?\s?[A-Za-z]+\s\d{1,3}:\d{1,3}(?:–\d{1,3})?)*"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return ""


def parse_bible_citations(pdf_file, year, out_dir):
    """Parse Bible citations from the liturgical calendar PDF"""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "daily_bible_citations_2026.csv"

    MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
    output_rows = []
    current_month = None

    with pdfplumber.open(pdf_file) as pdf:
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

                # Detect date line (e.g., "1 Tue" or "12 Fri")
                m = re.match(r"^(\d{1,2})\s+\w{3}", line)
                if not m:
                    continue
                day_num = int(m.group(1))

                try:
                    date_obj = datetime(year, current_month, day_num)
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
    fieldnames = ["Date", "BibleCitationShort", "SourceLine"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Completed: {len(output_rows)} rows written to {output_csv}")


def parse_us_holidays(pdf_file, year, out_dir):
    """
    Extract US holidays from the PDF and write to CSV.
    """
    US_HOLIDAYS = {
        "New Year’s Day": f"{year}-01-01",
        "Martin Luther King Jr. Day": f"{year}-01-19",
        "Washington’s Birthday": f"{year}-02-16",
        "Memorial Day": f"{year}-05-25",
        "Independence Day": f"{year}-07-04",
        "Labor Day": f"{year}-09-07",
        "Columbus Day": f"{year}-10-12",
        "Veterans Day": f"{year}-11-11",
        "Thanksgiving Day": f"{year}-11-26",
        "Christmas Day": f"{year}-12-25",
    }

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / f"us_holidays_{year}.csv"

    found = []
    with pdfplumber.open(pdf_file) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            for holiday, fixed_date in US_HOLIDAYS.items():
                if holiday in text:
                    for line in text.splitlines():
                        if holiday in line:
                            date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", line)
                            if date_match:
                                date_str = date_match.group(1)
                                date = datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
                            else:
                                date = fixed_date
                            found.append({
                                "Date": date,
                                "HolidayName": holiday,
                                "IsFederalHoliday": 1
                            })

    # Write CSV
    fieldnames = ["Date", "HolidayName", "IsFederalHoliday"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(found)

    print(f"Completed: {len(found)} holidays written to {output_csv}")
    return found



# ----------------------------
# CLI
# ----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build 2026 liturgical CSVs")
    parser.add_argument("year", type=int, help="Year to build (2026)")
    parser.add_argument("--input-pdf", required=True, help="Input PDF file")
    parser.add_argument("--out", default="data/", help="Output folder for CSV")
    args = parser.parse_args()

    day_rows = parse_day_data(args.input_pdf, args.year, args.out)
    generate_year_at_a_glance(day_rows, args.out)
    generate_weekly_index(day_rows, args.out)

    # Always generate Bible citations too
    parse_bible_citations(args.input_pdf, args.year, args.out)

    # Always generate US holidays too
    parse_us_holidays(args.input_pdf, args.year, args.out)