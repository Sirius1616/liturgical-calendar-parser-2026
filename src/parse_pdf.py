#!/usr/bin/env python
"""
src/parse_pdf.py
Parses USCCB_2026_Feast_Calendar_CLEAN.pdf starting at page 13 and returns a
pandas DataFrame with parsed fields. This is a best-effort implementation using PyMuPDF.
"""

import re
from typing import List, Dict
import fitz
import pandas as pd
from datetime import datetime
from .utils import clean_text, normalize_color, normalize_rank

COLOR_KEYWORDS = {'green','white','violet','red','rose'}


def blocks_for_page(page) -> List[Dict]:
    blocks = page.get_text('blocks')
    parsed = []
    for b in blocks:
        x0, y0, x1, y1, text, *_ = b
        text = text.strip()
        if not text:
            continue
        parsed.append({'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'text': text})
    parsed.sort(key=lambda t: (t['y0'], t['x0']))
    return parsed


def split_columns(blocks):
    if not blocks:
        return [], []
    centers = [ (b['x0']+b['x1'])/2 for b in blocks ]
    split_x = sum(centers)/len(centers)
    left = [b for b in blocks if (b['x0']+b['x1'])/2 <= split_x]
    right = [b for b in blocks if (b['x0']+b['x1'])/2 > split_x]
    return left, right


def guess_color_blocks(right_blocks):
    colors = []
    for b in right_blocks:
        txt = b['text']
        # crude: if any color keyword present, mark block
        if any(c in txt.lower() for c in COLOR_KEYWORDS):
            colors.append({'y0': b['y0'], 'y1': b['y1'], 'text': txt})
    return colors


def associate_color(y, color_blocks):
    best = None
    best_dist = 1e9
    for cb in color_blocks:
        if cb['y0'] <= y <= cb['y1']:
            return cb['text']
        dist = min(abs(cb['y0']-y), abs(cb['y1']-y))
        if dist < best_dist:
            best_dist = dist
            best = cb['text']
    return best


def parse_left_block_text(text: str) -> Dict:
    lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
    if not lines:
        return {}
    first = lines[0]
    # day number
    m = re.match(r'^(\d{1,2})', first)
    day_num = int(m.group(1)) if m else None
    # find readings line (pattern like Mt 4:12-17 or other verse tokens)
    readings = None
    readings_idx = None
    for i in range(len(lines)-1, -1, -1):
        ln = lines[i]
        if re.search(r"[A-Za-z]{1,3}\s+\d{1,3}:\d{1,3}", ln):
            readings = ln
            readings_idx = i
            break
    feast_lines = lines if readings_idx is None else lines[:readings_idx]
    feast_text = ' '.join(feast_lines)
    feast_text = clean_text(feast_text)
    rank = normalize_rank(feast_text)
    return {
        'display_date_number': day_num,
        'feast_primary_name': feast_text,
        'feast_rank': rank,
        'readings': readings
    }


def extract_calendar_data(pdf_path: str) -> pd.DataFrame:
    doc = fitz.open(pdf_path)
    entries = []
    for pidx in range(12, len(doc)):  # start at page 13 (index 12)
        page = doc[pidx]
        blocks = blocks_for_page(page)
        left_blocks, right_blocks = split_columns(blocks)
        color_blocks = guess_color_blocks(right_blocks)
        for lb in left_blocks:
            parsed = parse_left_block_text(lb['text'])
            if not parsed:
                continue
            ycenter = (lb['y0'] + lb['y1'])/2
            color_txt = associate_color(ycenter, color_blocks)
            color_norm = normalize_color(color_txt)
            entries.append({
                'display_date_number': parsed.get('display_date_number'),
                'feast_primary_name': parsed.get('feast_primary_name'),
                'feast_rank': parsed.get('feast_rank'),
                'liturgical_color': color_norm,
                'readings': parsed.get('readings'),
                'source_page': pidx + 1
            })
    df = pd.DataFrame(entries)
    return df
