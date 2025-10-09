import os
import pandas as pd

def test_bible_citations_exists():
    assert os.path.exists("data/daily_bible_citations_2026.csv")

def test_bible_citations_columns():
    df = pd.read_csv("data/daily_bible_citations_2026.csv")
    assert "Date" in df.columns
    assert "BibleCitationShort" in df.columns
