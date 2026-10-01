"""Fruit classifier (v0.0.1 trial).

Loads the BasicFruit CNN weights from cv/notebooks/basic_fruit.pth and runs
inference on an image to classify it into one of the trained classes.

The architecture and preprocessing MUST match the training notebook
(cv/notebooks/mixed_classification.ipynb) exactly:
  - input resized to 224x224, ToTensor only (NO normalization)
  - 3 classes: 0=apple, 1=banana, 2=tomato

torch is imported lazily and guarded so the backend still boots on hosts
without torch (e.g. Render free tier, where torch's memory is prohibitive).
When torch/weights are unavailable the caller degrades gracefully.
"""
import os
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)

# Classes in the exact order used during training (ThreeClassDataset labels).
CLASS_NAMES: List[str] = ["apple", "banana", "tomato"]

MODEL_VERSION = "v0.0.1 (trial)"

# Default weights path, resolved relative to the project root so it works
# regardless of the current working directory (repo root, backend/, Render).
_DEFAULT_WEIGHTS = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),  # backend/vision
        "..", "..",                                    # -> project root
        "cv", "notebooks", "basic_fruit.pth",
    )
)


class FruitClassifier:
    """Lazily loads torch + the BasicFruit weights and predicts fruit class."""

    def __init__(self, weights_path: str = None):
        self.weights_path = weights_path or os.getenv("CV_MODEL_PATH", _DEFAULT_WEIGHTS)
        self._model = None
        self._transform = None
        self._torch = None
        self._device = "cpu"
        self._load_error: str = ""
        self._loaded = False

    # ------------------------------------------------------------------
    def is_available(self) -> bool:
        """True if torch is installed and the weights file exists."""
        try:
            import torch  # noqa: F401
        except ImportError:
            self._load_error = "torch not installed"
            return False
        if not os.path.exists(self.weights_path):
            self._load_error = f"weights not found at {self.weights_path}"
            return False
        return True

    # ------------------------------------------------------------------
    def _build_model(self):
        """Recreate the BasicFruit architecture (must match training)."""
        torch = self._torch
        nn = torch.nn

        class BasicFruit(nn.Module):
            def __init__(self):
                super().__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(3, 32, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(kernel_size=2, stride=2),

                    nn.Conv2d(32, 64, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    nn.Dropout(0.25),

                    nn.Conv2d(64, 128, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    nn.Dropout(0.25),

                    nn.Conv2d(128, 128, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                )
                self.pool = nn.AdaptiveAvgPool2d((1, 1))
                self.classifier = nn.Sequential(
                    nn.Flatten(),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, 16),
                    nn.ReLU(),
                    nn.Linear(16, len(CLASS_NAMES)),
                )

            def forward(self, x):
                x = self.features(x)
                x = self.pool(x)
                x = self.classifier(x)
                return x

        return BasicFruit()

    # ------------------------------------------------------------------
    def _ensure_loaded(self):
        if self._loaded:
            return True
        if not self.is_available():
            raise RuntimeError(self._load_error or "CV classifier unavailable")

        import torch
        from torchvision import transforms

        self._torch = torch
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        model = self._build_model()
        state = torch.load(self.weights_path, map_location=self._device, weights_only=True)
        model.load_state_dict(state)
        model.to(self._device)
        model.eval()
        self._model = model

        # Preprocessing must mirror the training eval_transform exactly.
        self._transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
        self._loaded = True
        logger.info(f"FruitClassifier loaded (device={self._device}, version={MODEL_VERSION})")
        return True

    # ------------------------------------------------------------------
    def predict(self, image: Any) -> Tuple[str, float, Dict[str, float]]:
        """Classify a PIL image.

        Returns (class_name, top_confidence, {class_name: probability}).
        """
        self._ensure_loaded()
        torch = self._torch

        image = image.convert("RGB")
        tensor = self._transform(image).unsqueeze(0).to(self._device)

        with torch.no_grad():
            logits = self._model(tensor)
            probs = torch.softmax(logits, dim=1)[0]

        confidence, idx = torch.max(probs, dim=0)
        idx_int = int(idx.item())
        class_name = CLASS_NAMES[idx_int]
        prob_map = {name: round(float(probs[i].item()), 4) for i, name in enumerate(CLASS_NAMES)}

        return class_name, round(float(confidence.item()), 4), prob_map
