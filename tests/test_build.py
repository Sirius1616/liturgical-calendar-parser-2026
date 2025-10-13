import unittest
import tempfile
import csv
from pathlib import Path

from src.build import (
    classify_feast,
    next_month_name,
    generate_liturgical_calendar,
    generate_weekly_index,
    generate_us_holidays
)


class TestHelperFunctions(unittest.TestCase):
    def test_next_month_name(self):
        self.assertEqual(next_month_name("December"), "January")
        self.assertEqual(next_month_name("June"), "July")
        self.assertEqual(next_month_name("Invalid"), "Invalid")

    def test_classify_feast(self):
        self.assertEqual(classify_feast("Our Lady of Lourdes"), "Marian Feasts")
        self.assertEqual(classify_feast("Solemnity of the Lord"), "Solemnities of the Lord")
        self.assertEqual(classify_feast("Saint Peter"), "Major Saints")
        self.assertEqual(classify_feast("Some random day"), "Other Feasts")


class TestGenerateFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_csv = Path(tempfile.mktemp(suffix=".csv"))
        self.day_data = [
            ["2026-01-01", "Feast A", "", "white", 0, "", 0, 0, 1, 1, 1, 1, 12],
            ["2026-01-02", "Feast B", "", "green", 1, "New Year's Day", 0, 0, 1, 2, 2, 1, 12],
            ["2026-03-31", "Feast C", "", "violet", 0, "", 0, 0, 1, 3, 3, 1, 12],
        ]

    def tearDown(self):
        if self.temp_csv.exists():
            self.temp_csv.unlink()

    def test_generate_liturgical_calendar(self):
        generate_liturgical_calendar(self.day_data, self.temp_csv)
        with open(self.temp_csv) as f:
            reader = csv.reader(f)
            rows = list(reader)
        self.assertEqual(rows[0], ["Date", "DayOfMonth", "DayOfWeek", "LiturgicalColor"])
        self.assertEqual(rows[1][0], "2026-01-01")

    def test_generate_us_holidays(self):
        generate_us_holidays(self.day_data, self.temp_csv)
        with open(self.temp_csv) as f:
            reader = csv.reader(f)
            rows = list(reader)
        self.assertIn("HolidayName", rows[0])
        self.assertTrue(any("New Year's Day" in r for r in rows[1:]))

    def test_generate_weekly_index(self):
        generate_weekly_index(self.day_data, self.temp_csv)
        with open(self.temp_csv) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertIn("Season", rows[0])
        self.assertTrue(all("WeekStart" in r for r in rows))


if __name__ == "__main__":
    unittest.main()
