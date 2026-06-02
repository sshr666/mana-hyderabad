from __future__ import annotations

import argparse

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Mana Hyderabad civic YOLO model.")
    parser.add_argument("--model", default="cv/models/best.pt")
    parser.add_argument("--data", default="cv/dataset.yaml")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    metrics = YOLO(args.model).val(data=args.data, imgsz=args.imgsz, device=args.device, plots=True)
    print(f"Model: {args.model}")
    print(f"Dataset: {args.data}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall: {metrics.box.mr:.4f}")
    print(f"mAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"Outputs: {metrics.save_dir}")
    print("Report per-class weaknesses. Field verification remains required regardless of score.")


if __name__ == "__main__":
    main()
