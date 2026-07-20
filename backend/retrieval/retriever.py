from sentence_transformers import SentenceTransformer
from database.vector_database import VectorDatabase
import numpy as np
import re

db = VectorDatabase()
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

class Retriever:

    def __init__(self, db):
        self.db = db

    def _get_lexical_score(self, query, chunk_text):
        """Simple lexical overlap score."""
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words: return 0
        chunk_words = set(re.findall(r'\w+', chunk_text.lower()))
        overlap = query_words.intersection(chunk_words)
        return len(overlap) / len(query_words)

    def retrieve(self, retrieval_query, top_k=50):
        all_chunks = self.db.get_all_chunks()
        if not all_chunks:
            return []

        # 1. Semantic Similarity (Vector)
        query_embedding = model.encode(retrieval_query, show_progress_bar=False, convert_to_numpy=True)
        chunk_embeddings = np.array([c["embedding"] for c in all_chunks])

        query_norm = np.linalg.norm(query_embedding)
        chunk_norms = np.linalg.norm(chunk_embeddings, axis=1)
        semantic_similarities = np.dot(chunk_embeddings, query_embedding) / (chunk_norms * query_norm + 1e-9)

        # 2. Lexical Similarity (Keyword)
        lexical_scores = np.array([self._get_lexical_score(retrieval_query, c["text"]) for c in all_chunks])

        # 3. Hybrid Fusion (Alpha=0.7 vector, 0.3 lexical)
        hybrid_scores = (0.7 * semantic_similarities) + (0.3 * lexical_scores)

        results = []
        for i, score in enumerate(hybrid_scores):
            results.append((all_chunks[i], float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]