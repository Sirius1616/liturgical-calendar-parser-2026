# src/validate.py
import csv
from pathlib import Path
from datetime import datetime
from .schema import SCHEMAS

QC_REPORT = Path("reports/qc_2026.md")

def check_type(value, expected_type):
    """Check if a value matches the expected type"""
    if expected_type == "string":
        return isinstance(value, str) and value.strip() != ""
    if expected_type == "int":
        return value.isdigit()
    if expected_type == "date":
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except Exception:
            return False
    if isinstance(expected_type, list):  # enum check
        return value in expected_type
    return True  # fallback

def validate_csv(file_path, schema):
    """Validate a single CSV file against schema definition"""
    errors = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        # ✅ Check required fields
        for req in schema["required"]:
            if req not in headers:
                errors.append(f"Missing required field: {req}")

        # ✅ Row checks
        for i, row in enumerate(reader, start=2):  # row 2 = first data row
            for field, expected in schema["fields"].items():
                val = row.get(field, "")
                if not val:
                    if field in schema["required"]:
                        errors.append(f"Row {i}: Missing value for {field}")
                    continue
                if not check_type(val, expected):
                    errors.append(f"Row {i}: Invalid {field}='{val}' (expected {expected})")
    return errors

def main():
    report_lines = ["# QC Report for 2026 CSVs", ""]

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    for csv_name, schema in SCHEMAS.items():
        file_path = data_dir / csv_name
        if not file_path.exists():
            report_lines.append(f"❌ {csv_name} not found")
            continue

        errors = validate_csv(file_path, schema)
        if errors:
            report_lines.append(f"❌ {csv_name} has {len(errors)} issues:")
            report_lines.extend([f"   - {e}" for e in errors])
        else:
            report_lines.append(f"✅ {csv_name} passed validation")

        report_lines.append("")

    QC_REPORT.parent.mkdir(exist_ok=True)
    QC_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"QC report written to {QC_REPORT}")

if __name__ == "__main__"
    main()
