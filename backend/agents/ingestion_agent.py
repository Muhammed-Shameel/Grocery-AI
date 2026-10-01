import os
import json
import hashlib
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class IngestionAgent:
    """Agentic ingestion manager responsible for detecting new data, evaluating chunk quality,
    preventing duplicates, and incrementally updating the vector database."""
    
    def __init__(self, chroma_db: Any, embedder: Any, state_file: str = "backend/data/processed_state.json"):
        self.chroma_db = chroma_db
        self.embedder = embedder
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, str]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load ingestion state: {e}")
        return {}

    def _save_state(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def _compute_file_hash(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def evaluate_chunk_quality(self, chunk: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluates chunk quality to ensure it contains rich informative grocery/food knowledge."""
        text = chunk.get("text", "").strip()
        
        # Rule 1: Minimum length check
        if len(text) < 30:
            return False, "Chunk too short (< 30 characters)."
        
        # Rule 2: Boilerplate / Empty check
        lower_text = text.lower()
        boilerplate_terms = ["all rights reserved", "table of contents", "page 1 of", "copyright"]
        if any(term in lower_text for term in boilerplate_terms) and len(text) < 100:
            return False, "Boilerplate content detected."
        
        # Rule 3: Information density (must contain alphanumeric words)
        words = text.split()
        if len(words) < 5:
            return False, "Insufficient word count."

        return True, "Passed quality check."

    def detect_new_files(self, raw_dir: str) -> List[str]:
        """Scans raw data directory for new or modified files."""
        new_files = []
        if not os.path.exists(raw_dir):
            logger.warning(f"Raw directory not found: {raw_dir}")
            return new_files

        for root, _, files in os.walk(raw_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Skip directories or system files
                if file.startswith("."):
                    continue
                file_hash = self._compute_file_hash(file_path)
                
                if file_path not in self.state or self.state[file_path] != file_hash:
                    new_files.append(file_path)
                    self.state[file_path] = file_hash

        self._save_state()
        return new_files

    def ingest_chunks_incrementally(self, chunks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Incrementally ingests new chunks into ChromaDB with quality evaluation and duplicate prevention."""
        ids = []
        documents = []
        metadatas = []

        seen_content_hashes = set()
        stats = {
            "total_evaluated": len(chunks),
            "passed_quality": 0,
            "skipped_quality": 0,
            "skipped_duplicates": 0,
            "successfully_ingested": 0
        }

        for chunk in chunks:
            # 1. Quality Evaluation
            is_valid, reason = self.evaluate_chunk_quality(chunk)
            if not is_valid:
                stats["skipped_quality"] += 1
                continue
            stats["passed_quality"] += 1

            # 2. Duplicate Detection (Content Hash & ID)
            text = chunk.get("text", "")
            content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            
            if content_hash in seen_content_hashes:
                stats["skipped_duplicates"] += 1
                continue
            seen_content_hashes.add(content_hash)

            raw_id = chunk.get("id")
            if raw_id is not None:
                chunk_id = str(raw_id)
            else:
                chunk_id = f"{os.path.basename(str(chunk.get('source', 'unknown')))}_{hashlib.sha256(text.encode()).hexdigest()[:12]}"

            ids.append(chunk_id)
            documents.append(text)
            metadatas.append({
                "article": chunk.get("article", "Unknown"),
                "section": chunk.get("section", "General"),
                "source": chunk.get("source", "Unknown"),
            })

        if not ids:
            logger.info("No new unique, high-quality chunks to ingest.")
            return stats

        logger.info(f"Generating embeddings for {len(ids)} new chunks...")
        embeddings = self.embedder.embed_documents(documents)

        logger.info("Uploading new chunks to ChromaDB...")
        try:
            self.chroma_db.add_documents(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            stats["successfully_ingested"] = len(ids)
            logger.info(f"Incremental ingestion successful: {stats['successfully_ingested']} new chunks added.")
        except Exception as e:
            logger.error(f"Incremental ingestion failed: {e}")
            raise

        return stats
