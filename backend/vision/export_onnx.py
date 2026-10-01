"""One-time dev tool: export the BasicFruit PyTorch weights to ONNX.

Run this locally (where torch + torchvision are installed) to produce
cv/notebooks/basic_fruit.onnx, which the backend then uses on Render
(via onnxruntime) so image recognition works without PyTorch.

Usage (from the repo root):
    .venv/Scripts/python.exe backend/vision/export_onnx.py
"""
import os
import sys

# Make `backend/` importable so `from vision.fruit_classifier import ...` works
# regardless of the current working directory.
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BACKEND_DIR)

import numpy as np
import torch

from vision.fruit_classifier import FruitClassifier, CLASS_NAMES, IMG_SIZE


def main():
    torch.manual_seed(0)

    # Rebuild the architecture and load the trained weights (source of truth).
    clf = FruitClassifier()
    if not os.path.exists(clf.weights_path):
        raise SystemExit(f"Missing weights: {clf.weights_path}")

    clf._torch = torch
    model = clf._build_model()
    state = torch.load(clf.weights_path, map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()

    onnx_path = clf.onnx_path
    dummy = torch.zeros(1, 3, IMG_SIZE[0], IMG_SIZE[1], dtype=torch.float32)

    print(f"Exporting {clf.weights_path}  ->  {onnx_path}")
    torch.onnx.export(
        model,
        dummy,
        onnx_path,
        input_names=["input"],
        output_names=["logits"],
        opset_version=12,
        dynamo=False,          # use the stable TorchScript exporter (fixed batch)
        do_constant_folding=True,
    )
    size_kb = os.path.getsize(onnx_path) / 1024
    print(f"Wrote ONNX model ({size_kb:.1f} KB)")

    # --- Verify: same preprocessing must give matching predictions ----------
    import onnxruntime as ort
    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

    x = torch.rand(1, 3, IMG_SIZE[0], IMG_SIZE[1], dtype=torch.float32)
    with torch.no_grad():
        torch_logits = model(x).numpy()
    onnx_logits = session.run(None, {"input": x.numpy()})[0]

    max_diff = float(np.abs(torch_logits - onnx_logits).max())
    print(f"Max |torch - onnx| logits diff on random input: {max_diff:.6f}")
    if max_diff > 1e-3:
        raise SystemExit("ERROR: ONNX output diverges from PyTorch — check export.")

    # Report the predicted class ordering sanity.
    print(f"Classes (order preserved): {CLASS_NAMES}")
    print("ONNX export verified OK.")


if __name__ == "__main__":
    main()
