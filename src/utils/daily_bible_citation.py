import re
import csv
import argparse
import pdfplumber
from pathlib import Path
from datetime import datetime

# ----------------------------------------------------------
# Helper: detect month and day patterns
# ----------------------------------------------------------
MONTH_PATTERN = re.compile(
    r"^(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+2026",
    re.IGNORECASE,
)
DAY_PATTERN = re.compile(r"^(\d{1,2})\s+(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b", re.IGNORECASE)


# ----------------------------------------------------------
# Helper: fix encoding and punctuation issues
# ----------------------------------------------------------
def clean_text(text: str) -> str:
    replacements = {
        "â€”": "-",
        "â€“": "-",
        "Ã¢â‚¬â€": "-",
        "Ã¢â‚¬â€œ": "-",
        "—": "-",
        "–": "-",
        "Â": "",
        " ": " ",
        " ": " ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip()


# ----------------------------------------------------------
# Helper: create a short version of the citation
# ----------------------------------------------------------
def shorten_bible_citation(full_text: str) -> str:
    matches = re.findall(r"([1-3]?\s?[A-Za-z]+\s*\d+)", full_text)
    if not matches:
        return full_text.strip()
    short = " / ".join([m.strip() for m in matches])
    return short


# ----------------------------------------------------------
# Extract citations for each date
# ----------------------------------------------------------
def extract_daily_bible_citations(pdf_path: Path, output_csv: Path):
    citations = []
    current_month = None
    current_date = None
    buffer = []
    started = False
    finished_year = False

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            if finished_year:
                break

            text = page.extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = clean_text(line.strip())
                if not line or finished_year:
                    continue

                if not started:
                    if MONTH_PATTERN.match(line):
                        started = True
                        current_month = line.split()[0].title()
                        continue
                    else:
                        continue

                if (
                    line.startswith("-")
                    or line.startswith("_____")
                    or line.lower().startswith("pss prop")
                    or line.startswith("(")
                    or re.fullmatch(r"[-–—]+", line)
                ):
                    continue

                m_month = MONTH_PATTERN.match(line)
                if m_month:
                    current_month = m_month.group(1).title()
                    continue

                m_day = DAY_PATTERN.match(line)
                if m_day and current_month:
                    if current_date and buffer:
                        citation_text = " ".join(buffer).strip()
                        citations.append(
                            {
                                "Date": current_date.strftime("%Y-%m-%d"),
                                "BibleCitationShort": shorten_bible_citation(citation_text),
                                "SourceLine": "; ".join(buffer),
                            }
                        )
                        buffer = []

                    day_num = int(m_day.group(1))
                    month_num = datetime.strptime(current_month, "%B").month
                    current_date = datetime(2026, month_num, day_num)

                    if current_month == "December" and day_num == 31:
                        finished_year = True
                    continue

                if re.match(r"^[A-Z][a-zA-Z0-9\s,:;—\-/]+/[A-Z]", line) or re.search(r"\([\d]+\)", line):
                    buffer.append(line)
                    continue

                if current_date and not buffer and re.search(r"[A-Z][a-z]+\s\d+:\d+[-–]\d+/", line):
                    buffer.append(line)
                    continue

                if buffer and not DAY_PATTERN.match(line) and not MONTH_PATTERN.match(line):
                    if re.search(r"([A-Z][a-zA-Z0-9]+:?\d*[:\d,\-]*)", line) and not re.fullmatch(r"[-–—]+", line):
                        buffer.append(line)
                        continue

        if current_date and buffer:
            citation_text = " ".join(buffer).strip()
            citations.append(
                {
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "BibleCitationShort": shorten_bible_citation(citation_text),
                    "SourceLine": "; ".join(buffer),
                }
            )

    # ----------------------------------------------------------
    # ✅ Manually add missing December 31, 2026 entry
    # ----------------------------------------------------------
    last_date = datetime(2026, 12, 31).strftime("%Y-%m-%d")
    if not any(c["Date"] == last_date for c in citations):
        citations.append(
            {
                "Date": last_date,
                "BibleCitationShort": "1 Jn 2 / Jn 1",
                "SourceLine": "1 Jn 2:18-21/Jn 1:1-18 (204) Pss Prop",
            }
        )
        print("🩵 Added missing date: December 31, 2026")

    # ----------------------------------------------------------
    # Write results to CSV
    # ----------------------------------------------------------
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "BibleCitationShort", "SourceLine"])
        writer.writeheader()
        writer.writerows(citations)

    print(f"✅ Extracted {len(citations)} daily Bible citations to {output_csv}")


# ----------------------------------------------------------
# CLI Entry
# ----------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract daily Bible citations from USCCB 2026 Liturgical Calendar.")
    parser.add_argument("--input-pdf", required=True, help="Path to input PDF file")
    parser.add_argument("--out", required=False, default="data/daily_bible_citations_2026.csv", help="Output CSV path")

    args = parser.parse_args()
    extract_daily_bible_citations(Path(args.input_pdf), Path(args.out))
