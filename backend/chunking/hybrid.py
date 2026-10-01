import os
import json
import logging
from typing import List, Dict, Any

from recursive import RecursiveSectionMaker
from semantic import SemanticChunking

logger = logging.getLogger(__name__)

class HybridChunker:
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        embeddings: Any,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        source_type: str = None,
        output_filename: str = "semantic_chunks.json"
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.embeddings = embeddings
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.source_type = source_type
        self.output_filename = output_filename

    def chunk(self) -> List[Dict[str, Any]]:
        # Recursive
        recursive = (
            RecursiveSectionMaker(
                input_dir=self.input_dir,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            .load_documents()
            .recursive_split()
        )

        recursive_sections = recursive.get_sections()

        # Semantic
        semantic = (
            SemanticChunking(self.embeddings)
            .semantic_chunking(recursive_sections)
        )

        semantic_chunks = semantic.get_chunks()

        # Deterministic Duplicate Removal
        unique_chunks = self.remove_duplicates(semantic_chunks)

        # Save
        self.save_chunks(unique_chunks)

        return unique_chunks

    def remove_duplicates(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique = []
        for chunk in chunks:
            # Duplicates if they share source, section, and text
            identifier = (chunk['source'], chunk['section'], chunk['text'])
            if identifier not in seen:
                unique.append(chunk)
                seen.add(identifier)

        logger.info(f"Removed {len(chunks) - len(unique)} duplicate semantic chunks.")
        return unique

    def save_chunks(self, chunks: List[Dict[str, Any]]):
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, self.output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=4, ensure_ascii=False)

        logger.info(f"Saved {len(chunks)} chunks to {output_path}")