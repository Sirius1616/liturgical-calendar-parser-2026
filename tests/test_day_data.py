import os
import pandas as pd

def test_day_data_exists():
    assert os.path.exists("data/DAY_DATA.csv")

def test_day_data_columns():
    df = pd.read_csv("data/DAY_DATA.csv")
    expected = [
        "date", "feast_primary_name", "feast_rank", "liturgical_color",
        "is_holy_day_of_obligation", "us_holiday_name", "is_first_friday",
        "is_first_saturday", "week_row", "weekday_col", "display_date_number",
        "belongs_to_month", "source_page"
    ]
    assert list(df.columns) == expected
