import logging
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

class RetrievalAgent:
    """Manages retrieval of knowledge chunks from ChromaDB with subject filtering."""
    
    def __init__(self, retriever: Any, context_builder: Any):
        self.retriever = retriever
        self.context_builder = context_builder

    def retrieve_and_build_context(self, query: str, top_k: int = 5, subject: Optional[str] = None) -> Tuple[str, List[Tuple[Dict[str, Any], float]]]:
        """Retrieves relevant chunks and builds the context string with optional subject filter."""
        if not query or not query.strip():
            return "", []
        
        results = self.retriever.retrieve(query, top_k=top_k, subject=subject)
        context = self.context_builder.build(results)
        return context, results
