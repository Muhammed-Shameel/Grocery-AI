"""
pdf_to_text.py

Convert PDFs into clean, RAG-ready plain text, extracting tables into
separate JSON files.

Strictly excludes table regions from the body text.
"""

import argparse
import os
import re
import json
import fitz  # PyMuPDF

def extract_tables(page, page_num):
    results = []
    try:
        tabs = page.find_tables()
    except Exception:
        return results

    for i, tab in enumerate(tabs.tables):
        try:
            rows = tab.extract()
        except Exception:
            continue
        if not rows: continue
        
        headers = [str(c).strip() if c else "" for c in rows[0]]
        table_rows = [{headers[j]: (str(cell).strip() if cell else "") for j, cell in enumerate(row)} for row in rows[1:]]

        table_data = {
            "table_id": f"page_{page_num}_table_{i}",
            "page": page_num,
            "headers": headers,
            "rows": table_rows,
        }
        results.append((fitz.Rect(tab.bbox), table_data))
    return results

def extract_non_table_text(page, table_bboxes):
    """
    Strictly remove any text block overlapping table bounding boxes.
    """
    blocks = page.get_text("blocks")
    kept = []
    for b in blocks:
        rect = fitz.Rect(b[:4])
        text = b[4].strip()
        if not text: continue
        if any(rect.intersects(tb) for tb in table_bboxes):
            continue
        kept.append((rect, text))
    return kept

def order_reading_sequence(items, page_width):
    """
    Advanced spatial sorting using a grid-based approach to handle multi-column,
    floating objects, and complex layouts deterministically.
    """
    if not items: return []

    num_zones = 3
    zone_width = page_width / num_zones
    
    zones = [[] for _ in range(num_zones)]
    for item in items:
        # Determine zone index
        zone_idx = min(int(item[0].x0 / zone_width), num_zones - 1)
        zones[zone_idx].append(item)
    
    # Sort within each zone by vertical position (y0)
    for zone in zones:
        zone.sort(key=lambda it: it[0].y0)
        
    ordered = []
    for zone in zones:
        ordered.extend(zone)
    return ordered

def process_pdf(input_path):
    doc = fitz.open(input_path)
    all_tables = []
    full_text_lines = []

    for i, page in enumerate(doc):
        tables = extract_tables(page, i + 1)
        table_bboxes = [t[0] for t in tables]
        text_blocks = extract_non_table_text(page, table_bboxes)
        
        # Sort spatially using grid zones
        ordered_blocks = order_reading_sequence(text_blocks, page.rect.width)
        
        for _, text in ordered_blocks:
            # Basic cleanup of page-specific noise
            if len(text.strip()) < 3 and not text.strip().isalnum(): continue
            full_text_lines.append(text)
        all_tables.extend([t[1] for t in tables])
    
    doc.close()
    return "\n".join(full_text_lines), all_tables

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="backend/data/raw/pdf")
    parser.add_argument("--output_dir", default="backend/data/raw/pdf_text")
    parser.add_argument("--table_dir", default="backend/data_pipeline/clean/db_tables")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.table_dir, exist_ok=True)

    for filename in os.listdir(args.input_dir):
        if not filename.lower().endswith(".pdf"): continue
        
        text, tables = process_pdf(os.path.join(args.input_dir, filename))
        base_name = os.path.splitext(filename)[0]

        with open(os.path.join(args.output_dir, base_name + ".txt"), "w", encoding="utf-8") as f:
            f.write(text)
        if tables:
            with open(os.path.join(args.table_dir, base_name + "_tables.json"), "w", encoding="utf-8") as f:
                json.dump(tables, f, ensure_ascii=False, indent=4)
        print(f"Processed: {filename}")

if __name__ == "__main__":
    main()
