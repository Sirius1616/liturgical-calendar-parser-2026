import re
from datetime import datetime

# ----------------------------
# Basic Helpers
# ----------------------------
def is_first_friday(date_obj: datetime) -> bool:
    return date_obj.weekday() == 4 and date_obj.day <= 7

def is_first_saturday(date_obj: datetime) -> bool:
    return date_obj.weekday() == 5 and date_obj.day <= 7

def parse_feast_rank(text: str) -> str:
    for rank in ["Solemnity", "Feast", "Memorial", "Optional Memorial", "Weekday", "Sunday"]:
        if rank.lower() in text.lower():
            return rank
    return ""

def extract_color(text: str) -> str:
    pattern = r"(Green|White|Violet|Red|Rose)(\s*/\s*(Green|White|Violet|Red|Rose))?"
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        color = m.group(0).title().replace(" ", "")
        return color
    return ""

# ----------------------------
# Bible Citations
# ----------------------------
def extract_bible_citation(text: str) -> str:
    """Extract short Bible citation from a line"""
    pattern = r"\b(?:[1-3]?\s?[A-Za-z]+)\s\d{1,3}:\d{1,3}(?:–\d{1,3})?(?:;\s?[1-3]?\s?[A-Za-z]+\s\d{1,3}:\d{1,3}(?:–\d{1,3})?)*"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return ""
