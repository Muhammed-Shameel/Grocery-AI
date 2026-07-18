import os
import fitz
import json

input_dir = "backend/data/raw/pdf"
output_dir = "backend/data/raw/pdf_text"

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if not filename.endswith(".pdf"):
        continue
    input_path = os.path.join(input_dir, filename)
    
    doc = fitz.open(input_path)

    full_text = ""
    
    for page_number, page in enumerate(doc):
        
        text = page.get_text()
        
        full_text += text + "\n\n"

    output_filename = filename.replace(".pdf", ".txt")

    output_path = os.path.join(
        output_dir,
        output_filename
    )

    with open(output_path, "w", encoding="utf-8") as f:

        f.write(full_text)

    print(f"Saved: {output_filename}")