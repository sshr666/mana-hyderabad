from __future__ import annotations

import argparse

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Optionally export the civic YOLO model.")
    parser.add_argument("--model", default="cv/models/best.pt")
    parser.add_argument("--format", default="onnx", choices=["onnx", "torchscript"])
    args = parser.parse_args()
    output = YOLO(args.model).export(format=args.format)
    print(f"Exported model: {output}")
    print("Benchmark exported models before replacing PyTorch inference in production.")


if __name__ == "__main__":
    main()
