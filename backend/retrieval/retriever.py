from sentence_transformers import SentenceTransformer
from database.vector_database import VectorDatabase
import numpy as np

db = VectorDatabase()
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L3-v2")


class Retriever:

    def __init__(self, db):
        self.db = db

    def cosine_value(self, query_embedding, chunk_embedding):
        e_i = np.array(query_embedding)
        e_j = np.array(chunk_embedding)

        denominator = np.linalg.norm(e_i) * np.linalg.norm(e_j)

        if denominator == 0:
            return 0

        return float(np.dot(e_i, e_j) / denominator)

    def retrieve(self, question, top_k=5):

        query_embedding = model.encode(
            question,
            show_progress_bar=False,
            convert_to_numpy=True
        )

        results = []

        for chunk in self.db.get_all_chunks():

            chunk_embedding = chunk["embedding"]

            score = self.cosine_value(
                query_embedding,
                chunk_embedding
            )

            results.append((chunk, score))

        results.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return results[:top_k]