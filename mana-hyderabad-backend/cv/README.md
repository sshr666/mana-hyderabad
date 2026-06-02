# Mana Hyderabad Computer Vision

This folder contains the lightweight YOLO training and validation scaffold for four supported civic issue classes:

- `garbage_heap`
- `blocked_drain`
- `stagnant_water`
- `pothole`

Do not introduce aliases such as `trash`, `drain_block`, `standing_water`, or `road_hole`.

## Dataset Structure

```text
cv/data/images/train
cv/data/images/val
cv/data/images/test
cv/data/labels/train
cv/data/labels/val
cv/data/labels/test
```

Use a 70/20/10 train/validation/test split. Ensure each class appears in each split and avoid near-duplicate leakage.

## Annotation Format

Use YOLO detection labels. For each image, create a matching `.txt` file:

```text
class_id center_x center_y width height
```

Coordinates are normalized between `0` and `1`.

Class IDs:

- `0 = garbage_heap`
- `1 = blocked_drain`
- `2 = stagnant_water`
- `3 = pothole`

Example:

```text
0 0.512 0.481 0.244 0.310
1 0.701 0.623 0.182 0.214
```

## Collection Guidance

Use real or appropriately licensed images. Include daytime, low-light, rainy, dry, close-up, distant, partial-occlusion, and different mobile-camera angles. Add negative images with no target object.

Remove personal information where practical, avoid faces and vehicle plates where unnecessary, verify licensing, and keep a dataset manifest with source notes.

Prefer dataset quality over artificial count inflation. Do not claim production-grade accuracy from a small hackathon dataset.

## Commands

```bash
python cv/sanity_check.py --data cv/dataset.yaml
python cv/train.py --model yolo11n.pt --data cv/dataset.yaml --epochs 50 --imgsz 640 --batch 8 --device auto
python cv/validate.py --model cv/models/best.pt --data cv/dataset.yaml
python cv/predict_sample.py --model cv/models/best.pt --source cv/sample-images/sample.jpg
python cv/export_model.py --model cv/models/best.pt --format onnx
```

The local PyTorch model is sufficient for the MVP. Export can improve deployment portability later, but benchmark before switching.

## Licensing

Review the selected computer-vision library and dataset licenses before closed-source or commercial deployment. This note is not legal advice.
