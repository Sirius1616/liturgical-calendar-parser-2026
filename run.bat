@echo off
echo ==========================================
echo Running 2026 Calendar Data Extraction
echo ==========================================
python src\build_datasets.py
python src\validate.py
pause
