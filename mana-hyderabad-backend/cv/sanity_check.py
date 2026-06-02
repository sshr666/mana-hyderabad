from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import yaml


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate YOLO dataset structure and labels.")
    parser.add_argument("--data", default="cv/dataset.yaml")
    args = parser.parse_args()

    data = yaml.safe_load(Path(args.data).read_text())
    root = Path(data["path"])
    names = {int(key): value for key, value in data["names"].items()}
    distribution: dict[str, Counter] = {}
    errors: list[str] = []

    for split in ["train", "val", "test"]:
        image_dir = root / data[split]
        label_dir = root / data[split].replace("images", "labels")
        counter: Counter = Counter()
        images = [path for path in image_dir.glob("*") if path.suffix.lower() in IMAGE_EXTENSIONS]
        for image in images:
            label_file = label_dir / f"{image.stem}.txt"
            if not label_file.exists():
                errors.append(f"Missing label file: {label_file}")
                continue
            for line_number, row in enumerate(label_file.read_text().splitlines(), start=1):
                if not row.strip():
                    continue
                parts = row.split()
                if len(parts) != 5:
                    errors.append(f"Malformed row {label_file}:{line_number}")
                    continue
                class_id = int(parts[0])
                coords = [float(value) for value in parts[1:]]
                if class_id not in names:
                    errors.append(f"Unknown class id {class_id} in {label_file}:{line_number}")
                if any(value < 0 or value > 1 for value in coords):
                    errors.append(f"Coordinates outside 0..1 in {label_file}:{line_number}")
                counter[names.get(class_id, str(class_id))] += 1
        distribution[split] = counter

    for split, counter in distribution.items():
        print(f"{split}: {dict(counter)}")
    if errors:
        print("Dataset sanity check failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("Dataset sanity check passed.")


if __name__ == "__main__":
    main()
