import unittest
import tempfile
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.daily_bible_citation import (
    clean_text,
    shorten_bible_citation,
    extract_daily_bible_citations,
)


class TestDailyBibleCitationHelpers(unittest.TestCase):
    def test_clean_text(self):
        dirty = "â€”Â word–"
        cleaned = clean_text(dirty)
        self.assertNotIn("â€”", cleaned)
        self.assertNotIn("Â", cleaned)
        self.assertIn("-", cleaned)

    def test_shorten_bible_citation(self):
        full = "Gen 1:1-5 / Ps 23 / Mt 5:1-10"
        short = shorten_bible_citation(full)
        self.assertIn("Gen 1", short)
        self.assertIn("Ps 23", short)
        self.assertIn("Mt 5", short)


class TestExtractBibleCitations(unittest.TestCase):
    @patch("pdfplumber.open")
    def test_extract_daily_bible_citations(self, mock_pdfplumber):
        # Mock PDF pages
        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        JANUARY 2026
        1 Thu
        1 Jn 2:18-21/Jn 1:1-18 (204) Pss Prop
        2 Fri
        1 Jn 2:22-28/Jn 1:19-28 (205)
        """
        mock_pdfplumber.return_value.__enter__.return_value.pages = [mock_page]

        temp_csv = Path(tempfile.mktemp(suffix=".csv"))
        extract_daily_bible_citations(Path("fake.pdf"), temp_csv)

        with open(temp_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertGreater(len(rows), 0)
        self.assertIn("Date", rows[0])
        self.assertIn("BibleCitationShort", rows[0])
        temp_csv.unlink()


if __name__ == "__main__":
    unittest.main()
