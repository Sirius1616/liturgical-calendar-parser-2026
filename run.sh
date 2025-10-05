#!/bin/bash
echo "=========================================="
echo "Running 2026 Calendar Data Extraction"
echo "=========================================="
python3 src/build_datasets.py
python3 src/validate.py
