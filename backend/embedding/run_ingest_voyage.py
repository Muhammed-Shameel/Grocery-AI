"""Ingest Voyage-chunked data into the Voyage ChromaDB collection.

Parallel to run_ingest.py — same Ingester, but uses the Voyage API
embedder (no local model) and writes to a dedicated grocery_ai_voyage
collection so the existing local vector DB stays untouched.

Run from either the repo root or the backend/ directory:
    python backend/embedding/run_ingest_voyage.py
"""
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

# Support being run from repo root or from backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, BACKEND_DIR)

from embedding.chroma_db import ChromaDBManager
from embedding.ingest import Ingester
from embedding.voyage_embedder import VoyageEmbedder

embedder = VoyageEmbedder()

# Prefer Voyage-specific chunks if v4 chunking was run; otherwise reuse the
# existing v3 text chunks (chunk TEXTS are provider-agnostic — only the
# embeddings differ), so the free-tier API is never hammered re-chunking.
voyage_chunks = os.path.join(BACKEND_DIR, "data", "chunk_factory", "semantic_chunks_voyage.json")
fallback_chunks = os.path.join(BACKEND_DIR, "data", "chunk_factory", "semantic_chunks.json")
chunk_path = voyage_chunks if os.path.exists(voyage_chunks) else fallback_chunks
if not os.path.exists(chunk_path):
    raise FileNotFoundError(
        f"No chunk file found. Run backend/chunking/v4_chunk_maker_voyage.py "
        f"or ensure {fallback_chunks} exists."
    )
print(f"Using chunk file: {chunk_path}")

db = ChromaDBManager(
    db_path=os.path.join(BACKEND_DIR, "data", "vector_db"),
    embedder=embedder  # -> collection "grocery_ai_voyage"
)

# Optional hard reset (default OFF so the run is resumable). Set RESET_VOYAGE_DB=1
# to wipe and rebuild from scratch.
if os.getenv("RESET_VOYAGE_DB") == "1" and db.count() > 0:
    print(f"RESET_VOYAGE_DB=1 -> removing {db.count()} existing vectors...")
    db.delete_collection()
    db = ChromaDBManager(
        db_path=os.path.join(BACKEND_DIR, "data", "vector_db"),
        embedder=embedder
    )

(
    Ingester(
        chunk_path=chunk_path,
        embedder=embedder,
        chroma_db=db
    )
    .load_chunks()
    .ingest_resumable()
)

print(f"Total vectors in '{db.collection_name}': {db.count()}")
