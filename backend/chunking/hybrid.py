import os
import json

from recursive import RecursiveSectionMaker
from semantic import SemanticChunking


class HybridChunker:

    def __init__(
        self,
        input_dir,
        output_dir,
        embeddings,
        chunk_size=1000,
        chunk_overlap=200,
        source_type=None
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.embeddings = embeddings
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.source_type = source_type

    def chunk(self):

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

        # Save
        self.save_chunks(semantic_chunks)

        return semantic_chunks

    def save_chunks(self, chunks):

        os.makedirs(self.output_dir, exist_ok=True)

        output_path = os.path.join(
            self.output_dir,
            "semantic_chunks.json"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                chunks,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"Saved {len(chunks)} chunks")
        print(output_path)