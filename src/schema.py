# src/schema.py

SCHEMAS = {
    "DAY_DATA.csv": {
        "fields": {
            "date": "date",
            "feast_primary_name": "string",
            "feast_rank": "enum[Solemnity|Feast|Memorial|Optional Memorial|Weekday|Sunday|blank]",
            "liturgical_color": "enum[Green|White|Violet|Red|Rose|Dual]",
            "is_holy_day_of_obligation": "0|1",
            "us_holiday_name": "string",
            "is_first_friday": "0|1",
            "is_first_saturday": "0|1",
            "week_row": "int",
            "weekday_col": "1–7",
            "display_date_number": "1–31",
            "belongs_to_month": "0|1",
            "source_page": "int",
        },
        "required": ["date", "feast_primary_name", "feast_rank", "liturgical_color"],
        "primary_key": ["date"],
        "row_count": {"min": 365, "max": 372},
        "allow_empty_rows": False,
    },

    "liturgical_calendar_2026_simple.csv": {
        "fields": {
            "Date": "date",
            "DayOfMonth": "1–31",
            "DayOfWeek": "enum[Sun–Sat]",
            "LiturgicalColor": "string",
        },
        "required": ["Date", "DayOfMonth", "DayOfWeek", "LiturgicalColor"],
        "primary_key": ["Date"],
        "row_count": {"min": 365, "max": 372},
        "allow_empty_rows": False,
    },

    "major_feasts_2026.csv": {
        "fields": {
            "FeastDate": "string (e.g. Jan 4)",
            "FeastName": "string",
            "Category": "enum[Solemnities|Marian|Saints]",
        },
        "required": ["FeastDate", "FeastName", "Category"],
        "primary_key": ["FeastDate", "FeastName"],
        "row_count": {"min": 10, "max": 60},
        "allow_empty_rows": False,
    },

    "weekly_index_2026.csv": {
        "fields": {
            "WeekStart": "date (Mon)",
            "WeekEnd": "date (Sun)",
            "WeekLabel": "string",
            "LiturgicalWeekLabel": "string",
            "Season": "enum[Advent|Christmas|Lent|Easter|Ordinary]",
            "MonthForMiniCal": "YYYY-MM",
            "WeekNumberInYear": "1–53",
        },
        "required": ["WeekStart", "WeekEnd", "WeekLabel", "Season"],
        "primary_key": ["WeekStart"],
        "row_count": {"min": 52, "max": 54},
        "allow_empty_rows": False,
    },

    "daily_bible_citations_2026.csv": {
        "fields": {
            "Date": "date",
            "BibleCitationShort": "string (e.g. Mt 4:12–17)",
            "SourceLine": "string",
        },
        "required": ["Date", "BibleCitationShort"],
        "primary_key": ["Date"],
        "row_count": {"min": 365, "max": 372},
        "allow_empty_rows": False,
    },

    "us_holidays_2026.csv": {
        "fields": {
            "Date": "date",
            "HolidayName": "string",
            "IsFederalHoliday": "0|1",
        },
        "required": ["Date", "HolidayName", "IsFederalHoliday"],
        "primary_key": ["Date"],
        "row_count": {"min": 8, "max": 20},
        "allow_empty_rows": False,
    },
}
