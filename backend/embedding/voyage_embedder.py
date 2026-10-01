import os
import time
import logging
from typing import List

from dotenv import load_dotenv

# Ensure backend/.env is found regardless of the current working directory
# (repo root, backend/, or Render).
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

from embedding.embedding_service import EmbeddingService

# Configure logging
logger = logging.getLogger(__name__)

# voyage-4-lite produces 1024-dim vectors; the API allows up to 1000 inputs
# per request, but the free tier also caps at 10K tokens/min, so we keep
# batches small enough that even chunky batches stay under that ceiling.
VOYAGE_DIMENSION = 1024
VOYAGE_BATCH_SIZE = int(os.getenv("VOYAGE_BATCH_SIZE", "24"))

# Free Voyage keys (no payment method) are capped at 3 requests/minute.
# On a rate-limit hit we back off (exponential, capped) and retry so long
# batch jobs (chunking, ingestion) survive instead of crashing. Online
# queries never add artificial latency — they only back off when the API
# actually rejects the call.
VOYAGE_BATCH_INTERVAL = float(os.getenv("VOYAGE_BATCH_INTERVAL", "21"))
VOYAGE_MAX_RETRIES = int(os.getenv("VOYAGE_MAX_RETRIES", "8"))
VOYAGE_MAX_BACKOFF = float(os.getenv("VOYAGE_MAX_BACKOFF", "75"))


def _is_rate_limit_error(e: Exception) -> bool:
    msg = str(e).lower()
    return "rate limit" in msg or "rpm" in msg or "too many requests" in msg or "429" in msg


class VoyageEmbedder:
    """Drop-in replacement for Embedder backed by the Voyage AI API.

    No local model is loaded, which keeps memory usage tiny on hosting
    platforms like Render. Exposes the same interface as the local
    Embedder (embed_query / embed_documents) plus provider metadata used
    to pick the correct ChromaDB collection.
    """

    provider = "voyage"
    collection_name = "grocery_ai_voyage"
    dimension = VOYAGE_DIMENSION

    def __init__(self, model_name: str = "voyage-4-lite"):
        self.model_name = model_name
        api_key = os.getenv("VOYAGE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "VOYAGE_API_KEY is not set. Add it to backend/.env or the "
                "environment before using the Voyage embedder."
            )
        logger.info(f"Initializing VoyageEmbedder with model: {model_name} (no local model loaded)")
        self.service = EmbeddingService()

    def _call_with_retry(self, fn, *args, pacing_sleep: float = 0.0):
        """Execute a Voyage API call with adaptive rate-limit backoff.

        pacing_sleep is applied only between batch calls (offline jobs);
        on a 429/rate-limit error we back off exponentially and retry.
        """
        for attempt in range(VOYAGE_MAX_RETRIES):
            try:
                result = fn(*args)
                if pacing_sleep > 0:
                    time.sleep(pacing_sleep)
                return result
            except Exception as e:
                if _is_rate_limit_error(e) and attempt < VOYAGE_MAX_RETRIES - 1:
                    wait = min(5 * (2 ** attempt), VOYAGE_MAX_BACKOFF)
                    logger.warning(
                        f"Voyage rate limit hit, backing off {wait:.0f}s "
                        f"(attempt {attempt + 1}/{VOYAGE_MAX_RETRIES})..."
                    )
                    time.sleep(wait)
                    continue
                raise

    def _batched_embed(self, texts: List[str], input_type: str) -> List[List[float]]:
        """Embed texts in API-safe batches, preserving order."""
        embeddings: List[List[float]] = []
        for start in range(0, len(texts), VOYAGE_BATCH_SIZE):
            batch = texts[start:start + VOYAGE_BATCH_SIZE]
            if input_type == "query":
                # embed_query handles a single query
                embeddings.append(self._call_with_retry(self.service.embed_query, batch[0]))
            else:
                embeddings.extend(self._call_with_retry(
                    self.service.embed_documents, batch, pacing_sleep=VOYAGE_BATCH_INTERVAL
                ))
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query via the Voyage API."""
        return self._call_with_retry(self.service.embed_query, text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents using batched API calls."""
        logger.info(f"Generating {len(texts)} embeddings via Voyage API.")
        return self._batched_embed(texts, input_type="document")


class VoyageEmbeddings:
    """Minimal LangChain-style Embeddings adapter over VoyageEmbedder.

    This is what langchain_experimental's SemanticChunker needs, so the
    chunking step can run entirely through the API without loading a
    local sentence-transformers model.
    """

    def __init__(self, embedder: VoyageEmbedder = None):
        self.embedder = embedder or VoyageEmbedder()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedder.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embedder.embed_query(text)


def _voyage_health_check() -> bool:
    """Verify the Voyage API is reachable with one tiny embedding call."""
    try:
        vec = VoyageEmbedder().embed_query("health check")
        return isinstance(vec, list) and len(vec) > 0
    except Exception as e:
        logger.error(f"Voyage API health check failed: {e}")
        return False


def get_embedder():
    """Factory: choose the embedding provider for this deployment.

    Controlled by the EMBEDDING_PROVIDER env var:
      - "voyage" (default): API-based, no local model (Render-friendly).
        Falls back to the local Embedder automatically if the API call
        fails, so the workflow never breaks.
      - "local": force the sentence-transformers Embedder (legacy path).
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "voyage").strip().lower()

    if provider == "local":
        from embedding.embedder import Embedder
        logger.info("Using LOCAL sentence-transformers embedder (EMBEDDING_PROVIDER=local)")
        return Embedder()

    if _voyage_health_check():
        logger.info("Using VOYAGE API embedder (no local model loaded)")
        return VoyageEmbedder()

    logger.warning(
        "Voyage API unavailable — falling back to local sentence-transformers "
        "embedder. Check VOYAGE_API_KEY and network access."
    )
    from embedding.embedder import Embedder
    return Embedder()


def get_collection_name(embedder) -> str:
    """Return the ChromaDB collection matching the embedder's vector space.

    Local MiniLM (384-dim) and Voyage (1024-dim) vectors must never share a
    collection, so each provider gets its own isolated collection.
    """
    return getattr(embedder, "collection_name", "grocery_ai")
