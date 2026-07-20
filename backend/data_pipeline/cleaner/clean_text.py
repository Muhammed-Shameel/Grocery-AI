"""
clean_text.py

Orchestrates the conversion of extracted .txt files into clean,
context-aware, structured JSON documents.
"""

import argparse
import json
import os
from pdf_text_cleaner import PDFTextCleaner

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="backend/data/raw/pdf_text")
    parser.add_argument("--output_dir", default="backend/data_pipeline/clean/research")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    for filename in os.listdir(args.input_dir):
        if not filename.endswith(".txt"): continue
        
        input_path = os.path.join(args.input_dir, filename)
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        cleaner = PDFTextCleaner(text)
        sections = cleaner.detect_sections().get_sections()

        # Augment with additional required fields
        final_sections = []
        for i, sec in enumerate(sections):
            sec["section_id"] = f"section_{i:03d}"
            sec["content_flags"] = {
                "contains_table_reference": "table" in sec["text"].lower(),
                "contains_formula": sec["category"] == "formula_or_equation",
                "contains_sequence_data": sec["category"] == "sequence_data"
            }
            final_sections.append(sec)

        article = {
            "document": {
                "title": os.path.splitext(filename)[0],
                "source": filename,
                "source_type": "pdf"
            },
            "sections": final_sections
        }

        output_path = os.path.join(args.output_dir, os.path.splitext(filename)[0] + ".json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False, indent=4)

        print(f"Cleaned: {filename}")

if __name__ == "__main__":
    main()
