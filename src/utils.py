#!/usr/bin/env python

"""
src/utils.py
Helpers: text cleaning, normalization, calendar grid helpers
"""
import re
import pandas as pd

def ensure_dir(path: str):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)

        
def clean_text(text: str) -> str:
    if text is None:
        return ''
    return ' '.join(text.strip().split())


def normalize_color(raw: str) -> str:
    """
    Normalize liturgical colors.
    Handles dual colors (e.g., "violet/white"), capitalization, and edge cases.
    """
    if not raw or not raw.strip():
        return ""   # fallback if blank

    parts = raw.split("/")
    normed = []
    for sub in parts:
        sub = sub.strip()
        if not sub:
            continue
        toks = sub.split()
        tok = toks[0] if toks else ""
        if not tok:
            continue
        tok = tok.lower()
        if tok.startswith("vio"):
            normed.append("Violet")
        elif tok.startswith("whi"):
            normed.append("White")
        elif tok.startswith("gre"):
            normed.append("Green")
        elif tok.startswith("red"):
            normed.append("Red")
        elif tok.startswith("ros"):
            normed.append("Rose")
        else:
            normed.append(sub.title())
    return "/".join(normed)


def normalize_rank(feast_text: str) -> str:
    if not feast_text:
        return ''
    ranks = ['Solemnity','Feast','Memorial','Optional Memorial','Weekday','Sunday']
    for r in ranks:
        if re.search(r"\b" + re.escape(r) + r"\b", feast_text, re.I):
            return r
    return ''


def create_date_skeleton(year=2026):
    dates = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31')
    sk = pd.DataFrame({'date': dates})
    sk['display_date_number'] = sk['date'].dt.day
    # weekday_col: Sunday=1 ... Saturday=7
    sk['weekday_col'] = ((sk['date'].dt.weekday + 1) % 7) + 1
    return sk


def compute_week_row_for_month(df_month: pd.DataFrame) -> pd.DataFrame:
    df = df_month.copy()
    first_day = df['date'].min().replace(day=1)
    # weekday of first_day: Monday=0... Sunday=6; convert to Sunday-first offset
    start_wd = ((first_day.weekday() + 1) % 7) + 1
    start_offset = start_wd - 1
    df['week_row'] = ((df['display_date_number'] + start_offset - 1) // 7) + 1
    return df
