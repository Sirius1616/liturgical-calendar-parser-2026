import os
import pandas as pd

def test_major_feasts_exists():
    assert os.path.exists("data/major_feasts_2026.csv")

def test_major_feasts_columns():
    df = pd.read_csv("data/major_feasts_2026.csv")
    assert set(df.columns) == {"FeastDate", "FeastName", "Category"}
