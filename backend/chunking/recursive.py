from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SKIP_SECTIONS = {
    "references",
    "bibliography",
    "authors",
    "acknowledgements",
    "appendix",
    "table of contents",
    "contents",
    "index",
    "copyright"
}

class RecursiveSectionMaker:
    def __init__(
        self,
        input_dir: str,
        chunk_overlap: int = 250,
        chunk_size: int = 1000,
    ):
        self.input_dir = Path(input_dir)
        self.chunk_overlap = chunk_overlap
        self.chunk_size = chunk_size

        self.raw_documents: List[Dict[str, Any]] = []
        self.recursive_sections: List[Dict[str, Any]] = []
        self.global_recursive_counter = 0

    def load_documents(self):
        logger.info(f"Searching JSON files in: {self.input_dir}")
        json_files = list(self.input_dir.rglob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files.")

        for input_path in json_files:
            try:
                with open(input_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                filename = input_path.stem

                # Determine JSON structure
                if isinstance(data, list):
                    article_title = filename.capitalize()
                    sections = data
                elif isinstance(data, dict):
                    article_title = data.get("document", {}).get("title") or data.get("title") or filename.capitalize()
                    sections = data.get("sections", [data])
                else:
                    logger.warning(f"Skipping malformed JSON structure in {input_path}")
                    continue

                for section in sections:
                    title = section.get("title", "General")

                    # Robust Skip Logic
                    if title.lower().strip() in SKIP_SECTIONS or not section.get("rag_relevant", True) or section.get("category") == "noise":
                        continue

                    # Text Normalization
                    text = " ".join(section.get("text", "").split())
                    if not text:
                        continue

                    self.raw_documents.append({
                        "source": str(input_path),
                        "article": article_title,
                        "section": title,
                        "text": text
                    })
            except Exception as e:
                logger.error(f"Error processing {input_path}: {e}")

        logger.info(f"Loaded {len(self.raw_documents)} raw sections.")
        return self

    def recursive_split(self):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""]
        )

        tiny_chunks_removed = 0

        for section in self.raw_documents:
            chunks = splitter.split_text(section["text"])

            for chunk in chunks:
                # Word count filtering
                if len(chunk.split()) < 15:
                    tiny_chunks_removed += 1
                    continue

                self.recursive_sections.append({
                    **section,
                    "text": chunk,
                    "recursive_chunk_id": self.global_recursive_counter,
                    "total_recursive_chunks": len(chunks)
                })
                self.global_recursive_counter += 1

        logger.info(f"Recursive chunking complete. Generated {len(self.recursive_sections)} chunks. Tiny chunks removed: {tiny_chunks_removed}")
        return self

    def get_sections(self):
        return self.recursive_sections