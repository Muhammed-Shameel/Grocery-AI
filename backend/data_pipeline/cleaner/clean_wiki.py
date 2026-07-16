import os
import json
import re

input_dir = "data_pipeline/raw/wiki"
output_dir = "data_pipeline/clean/wiki"

os.makedirs(output_dir, exist_ok=True)

excluded_sections = {
    "references",
    "bibliography",
    "external links",
    "see also",
    "further reading",
    "notes",
    "sources"
}

for filename in os.listdir(input_dir):

    if not filename.endswith(".json"):
        continue

    input_path = os.path.join(input_dir, filename)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clean_sections = []

    for section in data["sections"]:

        section_title = section["title"].strip()
        section_text = section["text"].strip()

        # Remove empty sections
        if not section_text:
            continue

        # Remove unwanted Wikipedia sections
        if section_title.lower() in excluded_sections:
            continue

        # Remove citation markers such as [1], [2], [123]
        section_text = re.sub(
            r"\[\d+\]",
            "",
            section_text
        )

        clean_sections.append({
            "title": section_title,
            "text": section_text
        })

    clean_data = {
        "title": data["title"].strip(),
        "summary": data["summary"].strip(),
        "sections": clean_sections
    }

    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            clean_data,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(filename)