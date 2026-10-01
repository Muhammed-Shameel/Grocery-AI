import re
import logging
from typing import List, Any, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class Retriever:
    """Production-grade ChromaDB retriever."""
    def __init__(self, chroma_db_manager: Any, embedder: Any):
        self.db = chroma_db_manager
        self.embedder = embedder

    def _normalize_query(self, query: str) -> str:
        """Lightweight query normalization."""
        query = query.lower()
        query = re.sub(r'[^\w\s]', '', query)
        query = " ".join(query.split())
        return query

    def retrieve(self, query: str, top_k: int = 5, subject: Optional[str] = None) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieve top-k chunks using ChromaDB with optional subject metadata filtering."""
        normalized_query = self._normalize_query(query)
        query_embedding = self.embedder.embed_query(normalized_query)
        
        # Build query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"]
        }
        
        if subject and subject.strip() and subject != "All Subjects":
            query_params["where"] = {"article": subject}
        
        # ChromaDB query
        results = self.db.collection.query(**query_params)
        
        retrieved_results = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                doc = results["documents"][0][i]
                meta = results["metadatas"][0][i]
                raw_distance = results["distances"][0][i]
                # Chroma's default space is squared-L2. Voyage returns unit-
                # normalized vectors, so squared_L2 = 2 - 2*cosine and the
                # cosine similarity is exactly (1 - distance/2). Clamp to [0, 1]
                # so scores are a valid similarity for the grounding gate.
                score = max(0.0, min(1.0, 1.0 - raw_distance / 2.0))
                
                chunk = {
                    "text": doc,
                    **meta
                }
                retrieved_results.append((chunk, score))
            
        logger.info(f"Retrieved {len(retrieved_results)} chunks for query: {normalized_query[:30]}... [subject: {subject}]")
        return retrieved_results
