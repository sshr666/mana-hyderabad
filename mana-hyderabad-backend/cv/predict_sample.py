from __future__ import annotations

import argparse
import time

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Run sample prediction with a trained civic YOLO model.")
    parser.add_argument("--model", default="cv/models/best.pt")
    parser.add_argument("--source", required=True)
    parser.add_argument("--conf", type=float, default=0.45)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    started = time.perf_counter()
    results = YOLO(args.model).predict(source=args.source, conf=args.conf, device=args.device, save=True, verbose=False)
    duration_ms = int((time.perf_counter() - started) * 1000)
    for result in results:
        names = result.names
        for box in result.boxes:
            label = names[int(box.cls)]
            confidence = float(box.conf)
            xyxy = [round(float(value), 2) for value in box.xyxy[0]]
            print(f"{label}: {confidence:.2%} box={xyxy}")
        print(f"Annotated preview saved under: {result.save_dir}")
    print(f"Inference duration: {duration_ms} ms")


if __name__ == "__main__":
    main()
