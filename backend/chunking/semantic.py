from langchain_experimental.text_splitter import SemanticChunker
from typing import Any, List, Dict
import logging

# Configure logging
logger = logging.getLogger(__name__)

class SemanticChunking:
    def __init__(self, embeddings_model: Any):
        self.embeddings = embeddings_model
        self.semantic_chunks: List[Dict[str, Any]] = []

    def semantic_chunking(self, recursive_sections: List[Dict[str, Any]]):
        # Configure SemanticChunker explicitly
        # breakpoint_threshold_type='percentile' is generally more robust for varied document structures
        # breakpoint_threshold_amount=95 is a high threshold to minimize over-splitting
        splitter = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=95
        )

        for section in recursive_sections:
            chunks = splitter.split_text(section["text"])

            # Semantic chunking now uses the global recursive_chunk_id for deterministic semantic IDs
            for idx, chunk in enumerate(chunks):
                self.semantic_chunks.append({
                    **section,
                    "text": chunk.strip(),
                    "semantic_chunk_id": f"{section['recursive_chunk_id']}_{idx}",
                    "total_semantic_chunks": len(chunks)
                })

        logger.info(f"Semantic chunking complete. Generated {len(self.semantic_chunks)} chunks.")
        return self

    def get_chunks(self):
        return self.semantic_chunks