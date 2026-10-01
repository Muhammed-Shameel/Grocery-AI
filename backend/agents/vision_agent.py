import io
import base64
import logging
from typing import Optional, Dict, Any

from pydantic import BaseModel

from vision.fruit_classifier import FruitClassifier, MODEL_VERSION

logger = logging.getLogger(__name__)


class VisualObservation(BaseModel):
    object_detected: Optional[str] = None
    classification: Optional[str] = None
    variety: Optional[str] = None
    confidence: float = 0.0
    source: str = "computer_vision"
    status: str = "not_available"
    # --- v0.0.1 (trial) additions (additive; safe for existing consumers) ---
    model_version: Optional[str] = None
    probabilities: Optional[Dict[str, float]] = None


class VisionAgent:
    """Runs image classification with the trained BasicFruit CNN (v0.0.1 trial).

    Falls back gracefully when no image is provided, when torch/weights are
    unavailable (e.g. Render free tier), or when decoding/inference fails —
    the rest of the RAG workflow is never blocked by CV.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.classifier = FruitClassifier(weights_path=model_path) if model_path else FruitClassifier()
        # Do not load torch eagerly; check lightweight availability only.
        self.model_available = self.classifier.is_available()
        if self.model_available:
            logger.info(f"CV classifier available (weights: {self.classifier.weights_path}) [{MODEL_VERSION}]")
        else:
            logger.info(f"CV classifier unavailable: {self.classifier._load_error} [{MODEL_VERSION}]")

    @staticmethod
    def _decode_image(image_data: str):
        """Decode a data URL or raw base64 string into a PIL Image."""
        from PIL import Image

        raw = image_data.strip()
        # Strip the "data:image/...;base64," prefix if present.
        if raw.startswith("data:") and "," in raw:
            raw = raw.split(",", 1)[1]

        image_bytes = base64.b64decode(raw)
        return Image.open(io.BytesIO(image_bytes))

    def analyze_image(self, image_data: Optional[Any] = None) -> VisualObservation:
        """Classify the provided image; returns a VisualObservation."""
        if not image_data:
            return VisualObservation(
                object_detected=None,
                classification=None,
                confidence=0.0,
                status="no_image_provided",
                model_version=MODEL_VERSION,
            )

        if not self.model_available:
            return VisualObservation(
                object_detected="unknown_fruit_or_vegetable",
                classification=None,
                confidence=0.0,
                status="cv_unavailable",
                model_version=MODEL_VERSION,
            )

        try:
            image = self._decode_image(image_data)
            class_name, confidence, probabilities = self.classifier.predict(image)
            logger.info(f"CV [{MODEL_VERSION}] predicted {class_name} (conf={confidence})")
            return VisualObservation(
                object_detected=class_name,
                classification=class_name,
                variety=None,
                confidence=confidence,
                source="computer_vision",
                status="success",
                model_version=MODEL_VERSION,
                probabilities=probabilities,
            )
        except Exception as e:
            logger.error(f"CV inference error: {e}")
            return VisualObservation(
                object_detected=None,
                classification=None,
                confidence=0.0,
                status=f"error: {str(e)}",
                model_version=MODEL_VERSION,
            )
