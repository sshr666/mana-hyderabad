from __future__ import annotations

import argparse
import os
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune a lightweight YOLO model for civic issue detection.")
    parser.add_argument("--model", default=os.getenv("VISION_BASE_MODEL") or "yolo11n.pt")
    parser.add_argument("--data", default="cv/dataset.yaml")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default=os.getenv("VISION_DEVICE", "auto"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    device = "cpu" if args.device == "auto" else args.device
    model = YOLO(args.model)
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        seed=args.seed,
        project="cv/runs",
        name="mana-hyderabad-civic",
        exist_ok=False,
    )
    print(f"Training complete. Results: {results.save_dir}")
    print("Copy the best checkpoint to cv/models/best.pt before enabling backend inference.")


if __name__ == "__main__":
    main()
