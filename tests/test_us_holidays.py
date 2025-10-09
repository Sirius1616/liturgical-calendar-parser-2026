import os
import pandas as pd

def test_us_holidays_exists():
    assert os.path.exists("data/us_holidays_2026.csv")

def test_us_holidays_columns():
    df = pd.read_csv("data/us_holidays_2026.csv")
    assert set(df.columns) == {"Date", "HolidayName", "IsFederalHoliday"}
