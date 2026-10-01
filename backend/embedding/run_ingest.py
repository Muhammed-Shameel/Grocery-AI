from embedder import Embedder
from chroma_db import ChromaDBManager
from ingest import Ingester

embedder = Embedder()

db = ChromaDBManager(
    db_path="data/vector_db"
)

(
    Ingester(
        chunk_path="data/chunk_factory/semantic_chunks.json",
        embedder=embedder,
        chroma_db=db
    )
    .load_chunks()
    .ingest()
)

print(f"Total vectors: {db.count()}")