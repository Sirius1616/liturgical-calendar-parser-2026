#!/usr/bin/env python
"""
src/validate.py
Runs QC checks and writes reports/qc_2026.md
"""
import os
import pandas as pd
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')


def validate_and_report(year=2026, data_dir=None, report_dir=None):
    if data_dir is None:
        data_dir = DATA_DIR
    if report_dir is None:
        report_dir = REPORTS_DIR
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'qc_{year}.md')

    day_data_path = os.path.join(data_dir, 'DAY_DATA.csv')
    if not os.path.exists(day_data_path):
        raise FileNotFoundError(f"DAY_DATA.csv not found at {day_data_path}")

    df = pd.read_csv(day_data_path, parse_dates=['date'])
    lines = []
    lines.append('# QC Report – 2026 Calendar')
    lines.append('')
    lines.append('## Summary')
    lines.append(f'- Rows: {len(df)}')
    lines.append(f'- Date range: {df.date.min().strftime("%Y-%m-%d")} to {df.date.max().strftime("%Y-%m-%d")}')
    lines.append('')

    # Coverage check (in-month dates)
    inmonth = df[df['belongs_to_month']==1]
    coverage = inmonth['date'].nunique()
    if coverage == 365:
        lines.append('- ✅ Coverage: 365 in-month dates present')
    else:
        lines.append(f'- ❌ Coverage: {coverage} in-month dates present (expected 365)')

    # Duplicates
    if inmonth['date'].duplicated().any():
        lines.append('- ❌ Duplicate in-month dates found')
    else:
        lines.append('- ✅ No duplicate in-month dates')

    # Weekday integrity
    try:
        df['weekday_calc'] = ((pd.to_datetime(df['date']).dt.weekday + 1) % 7) + 1
        mism = (df['weekday_calc'] != df['weekday_col']).sum()
        if mism == 0:
            lines.append('- ✅ Weekday integrity: all rows match weekday_col')
        else:
            lines.append(f'- ❌ Weekday integrity: {mism} rows mismatch weekday_col')
    except Exception:
        lines.append('- ❌ Weekday integrity: error computing weekdays')

    # Enum checks for feast_rank
    allowed_ranks = {'Solemnity','Feast','Memorial','Optional Memorial','Weekday','Sunday',''}
    bad_ranks = set(df['feast_rank'].dropna().unique()) - allowed_ranks
    if bad_ranks:
        lines.append(f"- ❌ Enum violations (feast_rank): {', '.join(map(str,bad_ranks))}")
    else:
        lines.append('- ✅ feast_rank enums OK')

    # Enum checks for colors
    allowed_colors = {'Green','White','Violet','Red','Rose',''}
    bad_colors = set()
    for v in df['liturgical_color'].dropna().unique():
        for token in str(v).split('/'):
            if token.strip().capitalize() not in allowed_colors:
                bad_colors.add(v)
    if bad_colors:
        lines.append(f"- ❌ Enum violations (liturgical_color): {', '.join(bad_colors)}")
    else:
        lines.append('- ✅ liturgical_color enums OK')

    # First Friday/Saturday flags
    ff_issues = df[(df['is_first_friday']==1) & (pd.to_datetime(df['date']).dt.weekday != 4)]
    fs_issues = df[(df['is_first_saturday']==1) & (pd.to_datetime(df['date']).dt.weekday != 5)]
    if not ff_issues.empty:
        lines.append(f"- ❌ First Friday flags incorrect for {len(ff_issues)} rows")
    else:
        lines.append('- ✅ First Friday flags OK')
    if not fs_issues.empty:
        lines.append(f"- ❌ First Saturday flags incorrect for {len(fs_issues)} rows")
    else:
        lines.append('- ✅ First Saturday flags OK')

    # Moveables check placeholder
    lines.append('- ⚠ Moveables check: not implemented (requires canonical list from PDF)')

    # Citations check
    citations_path = os.path.join(data_dir, 'daily_bible_citations_2026.csv')
    if os.path.exists(citations_path):
        cdf = pd.read_csv(citations_path)
        caps = cdf[(cdf['BibleCitationShort'].notna()) & (cdf['BibleCitationShort'] == cdf['BibleCitationShort'].str.upper())]
        if len(caps) > 0:
            lines.append(f'- ❌ {len(caps)} BibleCitationShort entries are ALL CAPS')
        else:
            lines.append('- ✅ BibleCitationShort casing OK')
    else:
        lines.append('- ⚠ daily_bible_citations_2026.csv not present; skipping citation checks')

    lines.append('\n## Appendix')
    lines.append(f'- Generated: {datetime.utcnow().isoformat()} UTC')

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('Wrote QC report to', report_path)


if __name__ == '__main__':
    validate_and_report()
