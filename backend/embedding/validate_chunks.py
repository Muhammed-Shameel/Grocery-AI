from jsonschema import validate, ValidationError
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CHUNK_SCHEMA = {
    "type": "object",
    "properties": {
        "source": {"type": "string"},
        "article": {"type": "string"},
        "section": {"type": "string"},
        "text": {"type": "string"},
        "recursive_chunk_id": {"type": "integer"},
        "semantic_chunk_id": {"type": "string"},
        "total_semantic_chunks": {"type": "integer"}
    },
    "required": ["source", "article", "section", "text", "semantic_chunk_id"]
}

def validate_chunks(chunks: List[Dict[str, Any]]):
    """Validates a list of chunks against the schema."""
    logger.info(f"Validating {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        try:
            validate(instance=chunk, schema=CHUNK_SCHEMA)
        except ValidationError as e:
            logger.error(f"Validation failed for chunk {i}: {e.message}")
            raise ValueError(f"Invalid chunk data at index {i}: {e.message}")
    logger.info("All chunks validated successfully.")
