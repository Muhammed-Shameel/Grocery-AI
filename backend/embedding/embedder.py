from langchain_huggingface import HuggingFaceEmbeddings
import logging
from typing import List, Any

# Configure logging
logger = logging.getLogger(__name__)

class Embedder:
    """Production-grade wrapper for sentence-transformer embeddings."""
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.model_name = model_name
        logger.info(f"Initializing Embedder with model: {model_name}")

        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name
        )

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents using batch processing."""
        logger.info(f"Generating embeddings for {len(texts)} documents.")
        return self.embeddings.embed_documents(texts)