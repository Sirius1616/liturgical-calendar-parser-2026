import re
import csv
import argparse
import pdfplumber
from pathlib import Path
from datetime import datetime, timedelta
from src.utils.daily_bible_citation import extract_daily_bible_citations


# -------------------- HELPER FUNCTIONS -------------------- #

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

def classify_feast(name):
    name_lower = name.lower()
    if "virgin mary" in name_lower or "our lady" in name_lower:
        return "Marian Feasts"
    elif any(x in name_lower for x in ["lord", "epiphany", "corpus christi", "christ"]):
        return "Solemnities of the Lord"
    else:
        return "Major Saints"

# -------------------- DAY DATA EXTRACTION -------------------- #

def extract_day_data(pdf_path: Path, year: int = 2026, start_page: int = 12, end_page: int = None):
    day_data = []
    current_month = None
    previous_day_num = 0
    previous_date_obj = None

    holy_days = {
        "2026-01-01": "Mary, Mother of God",
        "2026-05-14": "Ascension of the Lord",
        "2026-08-15": "Assumption of the Blessed Virgin Mary",
        "2026-11-01": "All Saints",
        "2026-12-08": "Immaculate Conception",
        "2026-12-25": "Christmas"
    }

    us_holidays = {
        "2026-01-01": "New Year's Day",
        "2026-07-04": "Independence Day",
        "2026-11-26": "Thanksgiving Day",
        "2026-12-25": "Christmas Day"
    }

    last_feast_name = ""
    last_rank = ""
    last_color = ""
    last_is_holy_day = 0
    last_us_holiday = ""
    last_is_first_friday = 0
    last_is_first_saturday = 0

    with pdfplumber.open(pdf_path) as pdf:
        if end_page is None:
            end_page = len(pdf.pages)

        for page_num in range(start_page, end_page):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if not text:
                continue
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if not lines:
                continue

            # Detect month at top
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

            if not current_month:
                continue

            skip_rest_of_page = False

            for i, line in enumerate(lines):
                if re.match(r"^(?:[-=_]{3,})$", line.strip()):
                    skip_rest_of_page = True
                    break
                if re.match(r"^(Notes?|Footnotes?)[:\s]*$", line.strip(), re.IGNORECASE):
                    skip_rest_of_page = True
                    break

                # Match date + feast + color
                match = re.match(
                    r"^(\d{1,2})\s+(?:\w+\s+)?(.+?)\s+((?:white|red|green|violet|black|rose|gold)"
                    r"(?:\s*(?:/|or)\s*(?:white|red|green|violet|black|rose|gold))*)$",
                    line, re.IGNORECASE
                )
                if not match:
                    continue

                day_num, feast, color = match.groups()
                day_num = int(day_num)
                rank = ""

                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if re.search(r"(Feast|Memorial|Solemnity|Optional Memorial)", next_line, re.IGNORECASE):
                        rank = next_line.strip()

                if day_num < previous_day_num and not page_month:
                    current_month = next_month_name(current_month)
                previous_day_num = day_num

                try:
                    date_obj = datetime.strptime(f"{year} {current_month} {day_num}", "%Y %B %d")
                    date_str = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

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

                previous_date_obj = date_obj
                last_feast_name = feast.strip()
                last_rank = rank
                last_color = color.capitalize()
                last_is_holy_day = 1 if date_str in holy_days else 0
                last_us_holiday = us_holidays.get(date_str, "")
                last_is_first_friday = 1 if ((date_obj.weekday() + 1) % 7 + 1 == 6 and day_num <= 7) else 0
                last_is_first_saturday = 1 if ((date_obj.weekday() + 1) % 7 + 1 == 7 and day_num <= 7) else 0

                weekday_num = date_obj.weekday()
                weekday_col = ((weekday_num + 1) % 7) + 1
                week_row = (day_num - 1) // 7 + 1

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
                    1,
                    page_num + 1
                ]
                day_data.append(row)

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
                continue

    return day_data

def extract_day_data_split(pdf_path: Path, output_csv: Path, year: int = 2026):
    data1 = extract_day_data(pdf_path, year, start_page=12, end_page=22)
    data2 = extract_day_data(pdf_path, year, start_page=21, end_page=None)
    all_data = data1 + data2

    # Deduplicate
    seen = set()
    unique_data = []
    for row in all_data:
        date_str = row[0]
        if date_str not in seen:
            seen.add(date_str)
            unique_data.append(row)

    # Auto add March 30-31
    for day_num, feast_name in [(30, "Monday of Holy Week"), (31, "Tuesday of Holy Week")]:
        date_obj = datetime(year, 3, day_num)
        date_str = date_obj.strftime("%Y-%m-%d")
        if date_str not in seen:
            weekday_num = date_obj.weekday()
            weekday_col = ((weekday_num + 1) % 7) + 1
            week_row = (day_num - 1) // 7 + 1
            row = [
                date_str, feast_name, "", "violet", 0, "", 0, 0, week_row, weekday_col, day_num, 1, 23
            ]
            unique_data.append(row)
            seen.add(date_str)

    unique_data.sort(key=lambda r: datetime.strptime(r[0], "%Y-%m-%d"))

    # Write day_data.csv
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "date", "feast_primary_name", "feast_rank", "liturgical_color",
            "is_holy_day_of_obligation", "us_holiday_name", "is_first_friday",
            "is_first_saturday", "week_row", "weekday_col", "display_date_number",
            "belongs_to_month", "source_page"
        ])
        writer.writerows(unique_data)

    print(f"✅ DAY DATA rows → {output_csv}")

# -------------------- LITURGICAL CALENDAR -------------------- #

def generate_liturgical_calendar(day_data, output_csv):
    rows = []
    for row in day_data:
        date_obj = datetime.strptime(row[0], "%Y-%m-%d")
        rows.append([row[0], date_obj.day, date_obj.strftime("%A"), row[3]])
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "DayOfMonth", "DayOfWeek", "LiturgicalColor"])
        writer.writerows(rows)
    print(f"✅ Liturgical calendar saved: {output_csv}")

# -------------------- MAJOR FEASTS -------------------- #

def extract_major_feasts(pdf_path: Path, output_csv: Path):
    feasts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in [8, 9]:
            page = pdf.pages[page_num]
            lines = [line.strip() for line in page.extract_text().splitlines() if line.strip()]
            current_date = ""
            current_name = ""
            for line in lines:
                date_match = re.match(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})", line)
                if date_match:
                    if current_date and current_name:
                        feasts.append([current_date, current_name, classify_feast(current_name)])
                    current_date = f"{date_match.group(1)[:3]} {date_match.group(2)}"
                    current_name = line[date_match.end():].strip(" ,*")
                else:
                    if line.lower().startswith(("sunday", "fourth thursday")):
                        continue
                    current_name += " " + line.strip(" ,*")
            if current_date and current_name:
                feasts.append([current_date, current_name, classify_feast(current_name)])

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["FeastDate", "FeastName", "Category"])
        writer.writerows(feasts)
    print(f"✅ Major feasts saved: {output_csv}")

# -------------------- WEEKLY INDEX -------------------- #

def generate_weekly_index(day_data, output_csv):
    import csv
    from datetime import datetime, timedelta

    # Compute liturgical season and week label
    def easter_date(year):
        # Anonymous Gregorian algorithm
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19*a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2*e + 2*i - h - k) % 7
        m = (a + 11*h + 22*l) // 451
        month = (h + l - 7*m + 114) // 31
        day = ((h + l - 7*m + 114) % 31) + 1
        return datetime(year, month, day)

    year = 2026
    easter = easter_date(year)
    ash_wednesday = easter - timedelta(days=46)
    pentecost = easter + timedelta(days=49)
    christmas = datetime(year, 12, 25)
    advent_start = christmas - timedelta(days=(christmas.weekday() + 22))  # 4 Sundays before Christmas
    baptism_of_lord = datetime(year, 1, 11)

    weeks = {}
    for row in day_data:
        date_obj = datetime.strptime(row[0], "%Y-%m-%d")
        week_start = date_obj - timedelta(days=date_obj.weekday())
        week_end = week_start + timedelta(days=6)
        key = week_start.strftime("%Y-%m-%d")
        if key in weeks:
            continue

        # Determine season
        if week_start >= advent_start and week_start <= christmas:
            season = "Advent"
        elif week_start >= datetime(year, 12, 25) and week_start <= datetime(year + 1, 1, 9):
            season = "Christmas"
        elif week_start >= datetime(year, 1, 5) and week_start < ash_wednesday:
            season = "Ordinary Time"
        elif week_start >= ash_wednesday and week_start < easter:
            season = "Lent"
        elif week_start >= easter and week_start <= pentecost:
            season = "Easter"
        else:
            season = "Ordinary Time"

        # Week number in season
        season_weeks = [w for w in weeks.values() if w["Season"] == season]
        lit_week_num = len(season_weeks) + 1
        lit_week_label = f"Week {lit_week_num} of {season}"

        # Correct WeekLabel with full month/day for start and end
        week_label = f"Week of {week_start.strftime('%b %d')}-{week_end.strftime('%b %d')}"

        weeks[key] = {
            "WeekStart": week_start.strftime("%Y-%m-%d"),
            "WeekEnd": week_end.strftime("%Y-%m-%d"),
            "WeekLabel": week_label,
            "LiturgicalWeekLabel": lit_week_label,
            "Season": season,
            "MonthForMiniCal": week_start.strftime("%Y-%m"),
            "WeekNumberInYear": week_start.isocalendar()[1]
        }

    # Sort weeks by start date
    sorted_weeks = sorted(weeks.values(), key=lambda x: x["WeekStart"])

    # Write to CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(sorted_weeks[0].keys()))
        writer.writeheader()
        writer.writerows(sorted_weeks)

    print(f"✅ Weekly index saved: {output_csv}")


# -------------------- US HOLIDAYS -------------------- #

def generate_us_holidays(day_data, output_csv):
    rows = []
    for row in day_data:
        if row[5]:
            rows.append([row[0], row[5], 1])
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "HolidayName", "IsFederalHoliday"])
        writer.writerows(rows)
    print(f"✅ US holidays saved: {output_csv}")

# -------------------- MAIN -------------------- #

def main():
    parser = argparse.ArgumentParser(description="Extract multiple liturgical calendar datasets")
    parser.add_argument("year", type=int, default=2026)
    parser.add_argument("--input-pdf", required=True, help="Path to cleaned USCCB Feast Calendar PDF")
    parser.add_argument("--out-dir", required=True, help="Output directory for generated CSV files")
    args = parser.parse_args()

    year = args.year
    pdf_path = Path(args.input_pdf)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)

    # Define output paths
    day_data_csv = out_dir / "day_data.csv"
    bible_citations_csv = out_dir / f"daily_bible_citations_{year}.csv"
    liturgical_calendar_csv = out_dir / f"liturgical_calendar_{year}_simple.csv"
    major_feasts_csv = out_dir / f"major_feasts_{year}.csv"
    weekly_index_csv = out_dir / f"weekly_index_{year}.csv"
    us_holidays_csv = out_dir / f"us_holidays_{year}.csv"

    print("\n==============================")
    print(f"📘 LITURGICAL CALENDAR BUILDER ({year})")
    print("==============================\n")

    # 1️⃣ Extract and build the DAY DATA
    print("🔍 Step 1: Extracting day data...")
    extract_day_data_split(pdf_path, day_data_csv, year)

    # 2️⃣ Use the day data to extract Bible citations
    print("📖 Step 2: Extracting daily Bible citations...")
    extract_daily_bible_citations(pdf_path, bible_citations_csv)

    # 3️⃣ Load the day data into memory for other outputs
    print("📅 Step 3: Loading day data for dependent outputs...")
    day_data = []
    with open(day_data_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            day_data.append(row)

    # 4️⃣ Generate simplified liturgical calendar
    print("🌈 Step 4: Generating simple liturgical calendar...")
    generate_liturgical_calendar(day_data, liturgical_calendar_csv)

    # 5️⃣ Extract major feasts
    print("⭐ Step 5: Extracting major feasts...")
    extract_major_feasts(pdf_path, major_feasts_csv)

    # 6️⃣ Generate weekly index
    print("📆 Step 6: Generating weekly index...")
    generate_weekly_index(day_data, weekly_index_csv)

    # 7️⃣ Generate US holidays
    print("🇺🇸 Step 7: Generating US holidays...")
    generate_us_holidays(day_data, us_holidays_csv)

    print("\n✅ All datasets generated successfully!")
    print(f"📂 Output folder: {out_dir.resolve()}")

if __name__ == "__main__":
    main()
