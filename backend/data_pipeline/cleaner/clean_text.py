import os
import json

from pdf_text_cleaner import PDFTextCleaner


input_dir = "backend/data/raw/pdf_text"

output_dir = "backend/data_pipeline/clean/pdf_json"

os.makedirs(output_dir, exist_ok=True)


for filename in os.listdir(input_dir):

    if not filename.endswith(".txt"):

        continue


    input_path = os.path.join(

        input_dir,

        filename

    )


    with open(

        input_path,

        "r",

        encoding="utf-8"

    ) as f:

        text = f.read()


    try:

        cleaner = PDFTextCleaner(text)

        sections = (

            cleaner

            .extract_article_content()

            .remove_page_artifacts()

            .detect_sections()

            .clean_sections()

            .get_sections()

        )


    except ValueError as error:

        print(

            f"Skipped {filename}: {error}"

        )

        continue


    article = {

        "title": filename.replace(

            ".txt",

            ""

        ),

        "sections": sections

    }


    output_filename = filename.replace(

        ".txt",

        ".json"

    )


    output_path = os.path.join(

        output_dir,

        output_filename

    )


    with open(

        output_path,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            article,

            f,

            ensure_ascii=False,

            indent=4

        )


    print(

        f"Cleaned: {output_filename}"

    )