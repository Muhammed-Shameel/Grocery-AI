"""Fruit classifier (v0.0.2 — ONNX-first).

Runs image classification on the trained BasicFruit CNN.

Backends (auto-selected, so the SAME code works locally and on Render):
  1. ONNX Runtime  -> cv/notebooks/basic_fruit.onnx  (preferred if present)
     Lightweight (~tens of MB); the only option that fits Render's 512 MB
     free tier, since it avoids PyTorch entirely.
  2. PyTorch       -> cv/notebooks/basic_fruit.pth   (fallback when torch is
     installed, e.g. a local dev machine).

The exported graph and preprocessing MUST match the training notebook
(cv/notebooks/mixed_classification.ipynb) exactly:
  - input resized to 224x224, scaled to [0,1], CHW (NO mean/std normalization)
  - 3 classes: 0=apple, 1=banana, 2=tomato

Both heavy libraries (torch / onnxruntime) are imported lazily and guarded so
the backend still boots on hosts that have neither — the caller then degrades
gracefully with a clear "unavailable" message.
"""
import os
import logging
from typing import Dict, List, Tuple, Any, Optional

logger = logging.getLogger(__name__)

# Classes in the exact order used during training (ThreeClassDataset labels).
CLASS_NAMES: List[str] = ["apple", "banana", "tomato"]

MODEL_VERSION = "v0.0.1 (trial)"

# Paths resolved relative to the project root so they work from any CWD
# (repo root, backend/, Render). Overridable via env vars.
_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
)
_DEFAULT_WEIGHTS = os.path.normpath(
    os.path.join(_ROOT, "cv", "notebooks", "basic_fruit.pth")
)
_DEFAULT_ONNX = os.path.normpath(
    os.path.join(_ROOT, "cv", "notebooks", "basic_fruit.onnx")
)

IMG_SIZE = (224, 224)


class FruitClassifier:
    """Lazily loads an ONNX or PyTorch backend and predicts the fruit class."""

    def __init__(self, weights_path: str = None, onnx_path: str = None):
        self.weights_path = weights_path or os.getenv("CV_MODEL_PATH", _DEFAULT_WEIGHTS)
        self.onnx_path = onnx_path or os.getenv("CV_MODEL_ONNX_PATH", _DEFAULT_ONNX)
        self._torch = None
        self._model = None          # torch nn.Module
        self._session = None        # onnxruntime InferenceSession
        self._device = "cpu"
        self._backend: Optional[str] = None  # "onnx" | "torch"
        self._load_error: str = ""
        self._loaded = False

    # ------------------------------------------------------------------
    def _torch_available(self) -> bool:
        try:
            import torch  # noqa: F401
            return os.path.exists(self.weights_path)
        except ImportError:
            return False

    def _onnx_available(self) -> bool:
        try:
            import onnxruntime  # noqa: F401
            return os.path.exists(self.onnx_path)
        except ImportError:
            return False

    def is_available(self) -> bool:
        """True if any runnable backend + its model file exist."""
        if self._onnx_available():
            return True
        if self._torch_available():
            return True
        self._load_error = "no CV runtime available (need onnxruntime+basic_fruit.onnx or torch+basic_fruit.pth)"
        return False

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

        # Prefer ONNX (the deployable, low-memory path) when its file exists.
        if self._onnx_available():
            import onnxruntime as ort
            self._session = ort.InferenceSession(
                self.onnx_path, providers=["CPUExecutionProvider"]
            )
            self._backend = "onnx"
            self._loaded = True
            logger.info(f"FruitClassifier loaded via ONNX Runtime ({self.onnx_path}) [{MODEL_VERSION}]")
            return True

        if self._torch_available():
            import torch
            self._torch = torch
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            model = self._build_model()
            state = torch.load(self.weights_path, map_location=self._device, weights_only=True)
            model.load_state_dict(state)
            model.to(self._device)
            model.eval()
            self._model = model
            self._backend = "torch"
            self._loaded = True
            logger.info(f"FruitClassifier loaded via PyTorch (device={self._device}) [{MODEL_VERSION}]")
            return True

        raise RuntimeError(self._load_error or "CV classifier unavailable")

    # ------------------------------------------------------------------
    @staticmethod
    def _preprocess(image: Any):
        """PIL image -> float32 CHW array [1,3,224,224] scaled to [0,1].

        Mirrors the training eval transform (Resize(224) + ToTensor, NO
        normalization) without requiring torchvision, so it is identical for
        both the ONNX and PyTorch backends.
        """
        import numpy as np
        from PIL import Image

        img = image.convert("RGB").resize(IMG_SIZE, Image.BILINEAR)
        arr = np.asarray(img, dtype="float32") / 255.0   # HWC [0,1]
        arr = arr.transpose(2, 0, 1)[np.newaxis, ...]     # NCHW
        return np.ascontiguousarray(arr)

    @staticmethod
    def _softmax(logits) -> List[float]:
        import numpy as np
        arr = np.asarray(logits, dtype="float64").reshape(-1)
        m = arr.max()
        e = np.exp(arr - m)
        return (e / e.sum()).tolist()

    # ------------------------------------------------------------------
    def predict(self, image: Any) -> Tuple[str, float, Dict[str, float]]:
        """Classify a PIL image.

        Returns (class_name, top_confidence, {class_name: probability}).
        """
        self._ensure_loaded()
        tensor = self._preprocess(image)

        if self._backend == "onnx":
            input_name = self._session.get_inputs()[0].name
            logits = self._session.run(None, {input_name: tensor})[0]
            probs = self._softmax(logits)
        else:  # torch
            torch = self._torch
            with torch.no_grad():
                out = self._model(torch.from_numpy(tensor).to(self._device))
                probs = torch.softmax(out, dim=1)[0].tolist()

        idx = max(range(len(probs)), key=probs.__getitem__)
        confidence = probs[idx]
        class_name = CLASS_NAMES[idx]
        prob_map = {name: round(p, 4) for name, p in zip(CLASS_NAMES, probs)}

        return class_name, round(float(confidence), 4), prob_map
