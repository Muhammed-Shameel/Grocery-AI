import json
import os
import logging
from typing import List, Dict, Any
try:
    from validate_chunks import validate_chunks
except ModuleNotFoundError:
    from embedding.validate_chunks import validate_chunks

# Configure logging
logger = logging.getLogger(__name__)

class Ingester:
    def __init__(self, chunk_path: str, embedder: Any, chroma_db: Any):
        self.chunk_path = chunk_path
        self.embedder = embedder
        self.chroma_db = chroma_db
        self.chunks: List[Dict[str, Any]] = []

    def load_chunks(self):
        """Load and validate semantic chunks from JSON."""
        if not os.path.exists(self.chunk_path):
            raise FileNotFoundError(f"Chunk file not found: {self.chunk_path}")

        with open(self.chunk_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        # Pre-ingestion validation
        validate_chunks(self.chunks)

        logger.info(f"Loaded {len(self.chunks)} chunks from {self.chunk_path}")
        return self
    def ingest(self):
        """Embed chunks and store them in ChromaDB."""
        ids = []
        documents = []
        metadatas = []

        seen_chunks = set()
        duplicates_skipped = 0

        for chunk in self.chunks:
            # Deterministic ID generation: filename_recursive_semantic
            # The structure ensures uniqueness globally across all files
            chunk_id = (
                f"{os.path.basename(chunk['source'])}_{chunk['recursive_chunk_id']}_{chunk['semantic_chunk_id']}"
            )

            # Duplicate chunk detection
            chunk_content = (chunk['source'], chunk['section'], chunk['text'])
            if chunk_content in seen_chunks:
                duplicates_skipped += 1
                continue
            seen_chunks.add(chunk_content)

            ids.append(chunk_id)
            documents.append(chunk["text"])

            metadatas.append({
                "article": chunk["article"],
                "section": chunk["section"],
                "source": chunk["source"],
            })

        logger.info(f"Ingestion stats: Total={len(self.chunks)}, Uploading={len(ids)}, Skipped Duplicates={duplicates_skipped}")

        if not ids:
            logger.warning("No unique chunks to ingest.")
            return self

        logger.info("Generating embeddings...")
        embeddings = self.embedder.embed_documents(documents)
        logger.info(f"Generated {len(embeddings)} embeddings.")

        logger.info("Uploading to ChromaDB...")
        try:
            self.chroma_db.add_documents(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info("Ingestion successful.")
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise

        return self

    def _build_records(self):
        """Prepare (id, document, metadata) records with deterministic ids and
        duplicate detection. Shared by both ingest() and the resumable ingest."""
        records = []
        seen_chunks = set()
        duplicates_skipped = 0
        for chunk in self.chunks:
            chunk_id = (
                f"{os.path.basename(chunk['source'])}_{chunk['recursive_chunk_id']}_{chunk['semantic_chunk_id']}"
            )
            chunk_content = (chunk['source'], chunk['section'], chunk['text'])
            if chunk_content in seen_chunks:
                duplicates_skipped += 1
                continue
            seen_chunks.add(chunk_content)
            records.append((
                chunk_id,
                chunk["text"],
                {
                    "article": chunk["article"],
                    "section": chunk["section"],
                    "source": chunk["source"],
                },
            ))
        logger.info(f"Prepared {len(records)} unique records (skipped {duplicates_skipped} duplicates).")
        return records

    def ingest_resumable(self, batch_size: int = 24):
        """Embed + write in small checkpointed batches, skipping ids already
        present. Safe against API rate limits and re-runnable: if it aborts,
        simply run it again and it continues where it left off."""
        records = self._build_records()
        existing = self.chroma_db.get_existing_ids()
        pending = [r for r in records if r[0] not in existing]
        logger.info(f"Resumable ingest: {len(records)} total, {len(existing)} already stored, {len(pending)} to embed.")

        if not pending:
            logger.info("Nothing to ingest — collection already complete.")
            return self

        done = 0
        for start in range(0, len(pending), batch_size):
            group = pending[start:start + batch_size]
            ids = [r[0] for r in group]
            docs = [r[1] for r in group]
            metas = [r[2] for r in group]

            # embed_documents already paces + retries on rate limits internally.
            embeddings = self.embedder.embed_documents(docs)
            self.chroma_db.add_documents(
                ids=ids, documents=docs, embeddings=embeddings, metadatas=metas
            )
            done += len(ids)
            logger.info(f"Checkpoint: stored {done}/{len(pending)} new vectors (collection now {self.chroma_db.count()}).")

        logger.info(f"Resumable ingestion complete. Collection size: {self.chroma_db.count()}.")
        return self