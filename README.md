# Liturgical Calendar Parser 2026

A Python-based parser that extracts and structures data from the official **USCCB 2026 Liturgical Calendar PDF** into machine-readable formats (CSV/JSON).

## 📖 Overview

This project processes the United States Conference of Catholic Bishops' 2026 liturgical calendar, extracting detailed information about daily feasts, solemnities, memorials, and observances. The parsed data includes liturgical ranks, colors, holy days of obligation, and US holidays.

## ✨ Features

- **PDF Text Extraction**: Parses text from the USCCB 2026 Calendar PDF starting at page 13
- **Comprehensive Data Fields**:
  - Date (YYYY-MM-DD format)
  - Feast/Memorial primary name
  - Liturgical rank (Solemnity, Feast, Memorial, etc.)
  - Liturgical color (white, red, green, violet, rose)
  - Holy day of obligation indicator
  - US civil holidays
  - First Friday/First Saturday markers
  - Week and weekday positioning
  - Source page reference
- **Data Validation**: Schema-based validation for consistency
- **Multiple Export Formats**: CSV and JSON output
- **Extensible Architecture**: Modular design for easy enhancements

## 📂 Project Structure

```
liturgical-calendar-parser-2026/
├── data/                       # Raw and parsed data files
│   ├── calendar_2026.csv       # Parsed CSV output
│   └── calendar_2026.json      # Parsed JSON output
├── reports/                    # Generated reports and exports
├── src/
│   ├── __init__.py
│   ├── build.py                # Main builder/orchestrator
│   ├── validate.py             # Data validation module
│   ├── schema.py               # Field definitions and rules
│   └── utils/
│       ├── parse_pdf.py        # PDF extraction utilities
│       ├── parse_day.py        # Day entry parser
│       └── helpers.py          # Helper functions
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## ⚙️ Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/liturgical-calendar-parser-2026.git
   cd liturgical-calendar-parser-2026
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Place the PDF**:
   - Download the USCCB 2026 Liturgical Calendar PDF
   - Place it in the `data/` directory as `usccb_calendar_2026.pdf`

## ▶️ Usage

### Basic Parsing

Run the main parser to extract and process the calendar:

```bash
python src/build.py
```

This will:
1. Extract text from the calendar PDF (starting at page 13)
2. Parse each day's liturgical information
3. Generate structured output in `data/calendar_2026.csv`

### Validation

Validate the parsed dataset against the schema:

```bash
python src/validate.py
```

### Custom Options

```bash
# Specify custom PDF path
python src/build.py --pdf-path /path/to/calendar.pdf

# Export to JSON instead of CSV
python src/build.py --format json

# Validate and export
python src/build.py --validate
```

## 📊 Output Format

### CSV Sample

| date | feast_primary_name | feast_rank | liturgical_color | is_holy_day_of_obligation | us_holiday_name | is_first_friday | is_first_saturday |
|------|-------------------|------------|------------------|---------------------------|-----------------|-----------------|-------------------|
| 2026-01-01 | Mary, Mother of God | Solemnity | white | 1 | New Year's Day | 0 | 0 |
| 2026-01-02 | Basil the Great and Gregory Nazianzen | Memorial | white | 0 | | 1 | 0 |
| 2026-01-06 | Epiphany of the Lord | Solemnity | white | 0 | | 0 | 0 |

### JSON Sample

```json
{
  "2026-01-01": {
    "date": "2026-01-01",
    "feast_primary_name": "Mary, Mother of God",
    "feast_rank": "Solemnity",
    "liturgical_color": "white",
    "is_holy_day_of_obligation": true,
    "us_holiday_name": "New Year's Day",
    "is_first_friday": false,
    "is_first_saturday": false,
    "source_page": 13
  }
}
```

## 🛠 Dependencies

- **pdfplumber**: PDF text extraction
- **pandas**: Data manipulation and CSV generation
- **regex**: Advanced pattern matching
- **python-dateutil**: Date parsing utilities

See `requirements.txt` for complete dependency list with versions.

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 🚀 Roadmap

- [ ] Add support for multiple years (2025, 2027, etc.)
- [ ] Include Bible reading references
- [ ] Export to iCalendar (.ics) format
- [ ] Add multilingual support (Spanish, Latin)
- [ ] Web-based calendar viewer
- [ ] API endpoint for calendar queries
- [ ] Integration with church management systems

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guidelines
- Tests are included for new features
- Documentation is updated as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **USCCB** for providing the official liturgical calendar
- The Catholic Church for maintaining liturgical traditions
- Contributors and maintainers of open-source libraries used in this project

## 📧 Contact

For questions, suggestions, or issues:
- Open an issue on GitHub
- Email: [your-email@example.com]

## ⚖️ Disclaimer

This parser is an unofficial tool for educational and organizational purposes. For authoritative liturgical information, always consult the official USCCB resources and your local diocese.

---

**Made with ❤️ for the Catholic community**