import chromadb
import logging
from typing import List, Any

# Configure logging
logger = logging.getLogger(__name__)

class ChromaDBManager:
    """Production-grade ChromaDB manager."""
    def __init__(
        self,
        db_path: str,
        collection_name: str = "grocery_ai",
        embedder: Any = None
    ):
        # If an embedder is provided, align the collection with its vector
        # space (e.g. grocery_ai_voyage for Voyage API embeddings) so that
        # 384-dim local and 1024-dim Voyage vectors never mix.
        if embedder is not None:
            collection_name = getattr(embedder, "collection_name", collection_name)

        self.db_path = db_path
        self.collection_name = collection_name

        # Connect to the persistent database
        logger.info(f"Connecting to ChromaDB at {self.db_path}")
        self.client = chromadb.PersistentClient(path=self.db_path)

        # Create or load the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        logger.info(f"Collection '{self.collection_name}' initialized. Current size: {self.collection.count()}")

    def count(self) -> int:
        return self.collection.count()

    def get_existing_ids(self) -> set:
        """Return the set of ids already stored (used for resumable ingest)."""
        try:
            return set(self.collection.get(include=[]).get("ids", []))
        except Exception as e:
            logger.error(f"Failed to get existing ids: {e}")
            return set()

    def get_subjects(self) -> List[str]:
        """Extract unique articles/subjects from ChromaDB metadata."""
        try:
            data = self.collection.get(include=["metadatas"])
            metadatas = data.get("metadatas", [])
            subjects = set()
            for meta in metadatas:
                if meta and "article" in meta:
                    subjects.add(meta["article"])
            return sorted(list(subjects))
        except Exception as e:
            logger.error(f"Failed to get subjects: {e}")
            return []

    def peek(self, limit: int = 5) -> Any:
        return self.collection.peek(limit=limit)

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict[str, Any]]
    ):
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info(f"Successfully added {len(ids)} documents to collection.")
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            raise

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5
    ) -> Any:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

    def delete_collection(self):
        logger.warning(f"Deleting collection: {self.collection_name}")
        self.client.delete_collection(self.collection_name)