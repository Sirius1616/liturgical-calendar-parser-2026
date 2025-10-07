import re
import csv
from pathlib import Path
import pdfplumber

PDF_FILE = "USCCB_2026_Feast_Calendar_CLEAN.pdf"
OUTPUT_CSV = "data/major_feasts_2026.csv"
YEAR = 2026

def parse_major_feasts(pdf_path: str, year: int, out_file: str) -> None:
    """
    Extract Major Feasts (from pages 8/9) into major_feasts_YYYY.csv
    Columns: FeastDate, FeastName, Category
    """
    output_rows = []

    categories = {
        "Solemnities of the Lord": "Solemnities of the Lord",
        "Marian Feasts": "Marian Feasts",
        "Major Saints": "Major Saints",
    }

    current_category = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_num in [8, 9]:  # only pages 8 and 9
            if page_num >= len(pdf.pages):
                continue
            text = pdf.pages[page_num].extract_text()
            if not text:
                continue

            lines = text.split("\n")

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect category
                for cat in categories:
                    if line.startswith(cat):
                        current_category = categories[cat]
                        break
                if line in categories:
                    continue

                # Detect feast entry (date + name)
                # Example: "Jan 4 Epiphany of the Lord"
                m = re.match(r"^([A-Z][a-z]{2}\s+\d{1,2})\s+(.+)$", line)
                if m and current_category:
                    feast_date = m.group(1)
                    feast_name = m.group(2).strip()
                    output_rows.append(
                        {"FeastDate": feast_date, "FeastName": feast_name, "Category": current_category}
                    )

    # Write CSV
    Path("data").mkdir(parents=True, exist_ok=True)
    fieldnames = ["FeastDate", "FeastName", "Category"]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"✅ Completed: {len(output_rows)} rows written to {out_file}")


if __name__ == "__main__":
    parse_major_feasts(PDF_FILE, YEAR, OUTPUT_CSV)
