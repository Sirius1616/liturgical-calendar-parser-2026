#!/bin/bash
set -e
echo "Running build_datasets..."
python -m src.build_datasets --input input/USCCB_2026_Feast_Calendar_CLEAN.pdf --out data/
echo "Running validate..."
python -m src.validate --data data/ --report reports/qc_2026.md

echo "Done. CSVs in /data and QC report in /reports/"
