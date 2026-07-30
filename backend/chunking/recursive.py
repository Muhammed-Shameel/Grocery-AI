from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
import os


class RecursiveSectionMaker:
    def __init__(
        self,
        input_dir,
        chunk_overlap=250,
        chunk_size=1000,
    ):
        self.input_dir = Path(input_dir)
        self.chunk_overlap = chunk_overlap
        self.chunk_size = chunk_size

        self.raw_documents = []
        self.recursive_sections = []

    def load_documents(self):

        print(f"\nSearching JSON files in:\n{self.input_dir}\n")

        json_files = list(self.input_dir.rglob("*.json"))

        print(f"Found {len(json_files)} JSON files.\n")

        for input_path in json_files:

            print(f"Loading: {input_path}")

            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            filename = input_path.stem

            # -------------------------
            # Determine JSON structure
            # -------------------------

            if isinstance(data, list):

                article_title = filename.capitalize()
                sections = data

            elif isinstance(data, dict):

                if "document" in data and "title" in data["document"]:
                    article_title = data["document"]["title"]

                elif "title" in data:
                    article_title = data["title"]

                else:
                    article_title = filename.capitalize()

                sections = data.get("sections", [data])

            else:
                continue

            # -------------------------
            # Store sections
            # -------------------------

            for section in sections:

                if not section.get("rag_relevant", True):
                    continue

                if section.get("category") == "noise":
                    continue

                self.raw_documents.append({
                    "source_type": input_path.parent.name,
                    "source": str(input_path),
                    "article": article_title,
                    "section": section.get("title", "General"),
                    "text": section.get("text", "")
                })

        print(f"\nLoaded {len(self.raw_documents)} raw sections.\n")

        return self

    def recursive_split(self):

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                "! ",
                "? ",
                "; ",
                ", ",
                " ",
                ""
            ]
        )

        print("Starting recursive chunking...\n")

        for section in self.raw_documents:

            chunks = splitter.split_text(section["text"])

            print(
                f'{section["article"]} | {section["section"]} '
                f'-> {len(chunks)} chunks'
            )

            for idx, chunk in enumerate(chunks):

                new_chunk = section.copy()

                new_chunk["text"] = chunk
                new_chunk["recursive_chunk_id"] = idx
                new_chunk["total_recursive_chunks"] = len(chunks)

                self.recursive_sections.append(new_chunk)

        print(
            f"\nGenerated {len(self.recursive_sections)} recursive chunks.\n"
        )

        return self

    def get_sections(self):
        return self.recursive_sections