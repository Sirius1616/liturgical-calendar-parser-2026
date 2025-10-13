import re
import csv
import argparse
import pdfplumber
from pathlib import Path
from datetime import datetime, timedelta


def extract_day_data(pdf_path: Path, output_csv: Path, year: int = 2026):
    day_data = []
    print(f"📘 Opening PDF: {pdf_path}")

    current_month = None
    previous_day_num = 0
    previous_date_obj = None

    # Define known US Holy Days of Obligation for 2026
    holy_days = {
        "2026-01-01": "Mary, Mother of God",
        "2026-05-14": "Ascension of the Lord",
        "2026-08-15": "Assumption of the Blessed Virgin Mary",
        "2026-11-01": "All Saints",
        "2026-12-08": "Immaculate Conception",
        "2026-12-25": "Christmas"
    }

    # Define US civil holidays (for reference)
    us_holidays = {
        "2026-01-01": "New Year's Day",
        "2026-07-04": "Independence Day",
        "2026-11-26": "Thanksgiving Day",
        "2026-12-25": "Christmas Day"
    }

    # Variables to track previous feast row for missing day injection
    last_feast_name = ""
    last_rank = ""
    last_color = ""
    last_is_holy_day = 0
    last_us_holiday = ""
    last_is_first_friday = 0
    last_is_first_saturday = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(13, len(pdf.pages)):  # Start from page 14
            page = pdf.pages[page_num]
            text = page.extract_text()
            if not text:
                continue

            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if not lines:
                continue

            # Detect month name at top of page
            page_month = None
            for line in lines[:5]:
                month_match = re.search(
                    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b",
                    line, re.IGNORECASE
                )
                if month_match:
                    page_month = month_match.group(1).capitalize()
                    break

            if page_month:
                current_month = page_month
                print(f"📅 Page {page_num+1}: Detected month → {current_month}")
            elif not current_month:
                continue

            skip_rest_of_page = False  # flag to detect when to skip rest of page

            for i, line in enumerate(lines):
                # Detect footnote or separator lines (e.g., "———", "_____", "=====")
                if re.match(r"^(?:[-=_]{3,})$", line.strip()):
                    print(f"⚠️ Footnote separator detected on page {page_num+1}, skipping rest of page")
                    skip_rest_of_page = True
                    break

                # Detect "Notes" or "Footnotes" section headers
                if re.match(r"^(Notes?|Footnotes?)[:\s]*$", line.strip(), re.IGNORECASE):
                    print(f"⚠️ Footnote section detected on page {page_num+1}, skipping rest of page")
                    skip_rest_of_page = True
                    break

                # Match date + feast + color pattern
                match = re.match(
                    r"^(\d{1,2})\s+(?:\w+\s+)?(.+?)\s+((?:white|red|green|violet|black|rose|gold)"
                    r"(?:\s*(?:/|or)\s*(?:white|red|green|violet|black|rose|gold))*)$",
                    line, re.IGNORECASE
                )
                if not match:
                    continue  # Skip non-feast lines

                day_num, feast, color = match.groups()
                day_num = int(day_num)
                rank = ""

                # Handle rank on next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if re.search(r"(Feast|Memorial|Solemnity|Optional Memorial)", next_line, re.IGNORECASE):
                        rank = next_line.strip()

                # Detect month rollover
                if day_num < previous_day_num and not page_month:
                    current_month = next_month_name(current_month)
                previous_day_num = day_num

                # Format date
                try:
                    date_obj = datetime.strptime(f"{year} {current_month} {day_num}", "%Y %B %d")
                    date_str = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

                # Inject missing days if gap detected
                if previous_date_obj:
                    delta = (date_obj - previous_date_obj).days
                    for d in range(1, delta):
                        missing_date_obj = previous_date_obj + timedelta(days=d)
                        missing_date_str = missing_date_obj.strftime("%Y-%m-%d")
                        missing_row = [
                            missing_date_str,
                            last_feast_name,
                            last_rank,
                            last_color,
                            last_is_holy_day,
                            last_us_holiday,
                            last_is_first_friday,
                            last_is_first_saturday,
                            (missing_date_obj.day - 1) // 7 + 1,
                            ((missing_date_obj.weekday() + 1) % 7) + 1,
                            missing_date_obj.day,
                            1,
                            page_num + 1
                        ]
                        day_data.append(missing_row)

                # Store current row info for potential injection
                previous_date_obj = date_obj
                last_feast_name = feast.strip()
                last_rank = rank
                last_color = color.capitalize()
                last_is_holy_day = 1 if date_str in holy_days else 0
                last_us_holiday = us_holidays.get(date_str, "")
                last_is_first_friday = 1 if ((date_obj.weekday() + 1) % 7 + 1 == 6 and day_num <= 7) else 0
                last_is_first_saturday = 1 if ((date_obj.weekday() + 1) % 7 + 1 == 7 and day_num <= 7) else 0

                # Compute weekday and week row
                weekday_num = date_obj.weekday()  # Monday=0 … Sunday=6
                weekday_col = ((weekday_num + 1) % 7) + 1  # Sunday=1 … Saturday=7
                week_row = (day_num - 1) // 7 + 1
                belongs_to_month = 1

                # Build row
                row = [
                    date_str,
                    feast.strip(),
                    rank,
                    color.capitalize(),
                    last_is_holy_day,
                    last_us_holiday,
                    last_is_first_friday,
                    last_is_first_saturday,
                    week_row,
                    weekday_col,
                    day_num,
                    belongs_to_month,
                    page_num + 1
                ]
                day_data.append(row)

            # 🧹 If footnote detected — reset trackers to avoid carryover
            if skip_rest_of_page:
                previous_date_obj = None
                previous_day_num = 0
                last_feast_name = ""
                last_rank = ""
                last_color = ""
                last_is_holy_day = 0
                last_us_holiday = ""
                last_is_first_friday = 0
                last_is_first_saturday = 0
                continue  # Move on to next page

    print(f"📝 Extracted {len(day_data)} raw rows")

    # Deduplicate and sort
    seen = set()
    unique_data = []
    for row in day_data:
        date_str = row[0]
        if date_str not in seen:
            seen.add(date_str)
            unique_data.append(row)

    unique_data.sort(key=lambda r: datetime.strptime(r[0], "%Y-%m-%d"))
    print(f"✅ Final output: {len(unique_data)} rows → {output_csv}")

    # Write CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "date", "feast_primary_name", "feast_rank", "liturgical_color",
            "is_holy_day_of_obligation", "us_holiday_name", "is_first_friday",
            "is_first_saturday", "week_row", "weekday_col", "display_date_number",
            "belongs_to_month", "source_page"
        ])
        writer.writerows(unique_data)


def next_month_name(current):
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    try:
        idx = months.index(current)
        return months[(idx + 1) % 12]
    except ValueError:
        return current


def main():
    parser = argparse.ArgumentParser(description="Extract DAY DATA from liturgical calendar PDF")
    parser.add_argument("--input-pdf", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--year", type=int, default=2026)
    args = parser.parse_args()
    extract_day_data(Path(args.input_pdf), Path(args.output_csv), args.year)


if __name__ == "__main__":
    main()
