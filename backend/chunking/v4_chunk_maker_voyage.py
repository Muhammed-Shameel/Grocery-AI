"""Voyage-API-based chunk maker (v4).

Identical workflow to v3_chunk_maker.py, but the SemanticChunker runs on
Voyage API embeddings instead of a locally loaded sentence-transformers
model. Output is written to semantic_chunks_voyage.json so the v3 file
is never overwritten.

Run from either the repo root or the backend/ directory:
    python backend/chunking/v4_chunk_maker_voyage.py
"""
import os
import sys

# Support being run from repo root or from backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, BACKEND_DIR)
# hybrid.py uses legacy bare-sibling imports (recursive, semantic)
sys.path.insert(0, BASE_DIR)

from hybrid import HybridChunker
from embedding.voyage_embedder import VoyageEmbeddings

# Root directory containing ALL cleaned JSON folders
input_dir = os.path.join(BACKEND_DIR, "data_pipeline", "clean")

# Where the semantic chunks will be saved
output_dir = os.path.join(BACKEND_DIR, "data", "chunk_factory")

# Embeddings via the Voyage API (no local model loaded)
embeddings = VoyageEmbeddings()

hybrid = HybridChunker(
    input_dir=input_dir,
    output_dir=output_dir,
    embeddings=embeddings,
    chunk_size=1500,
    chunk_overlap=300,
    output_filename="semantic_chunks_voyage.json"
)

chunks = hybrid.chunk()

print(f"Generated {len(chunks)} Voyage-based chunks -> {os.path.join(output_dir, 'semantic_chunks_voyage.json')}")
