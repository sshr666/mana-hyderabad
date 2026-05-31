import sys
from pathlib import Path
from typing import Any

import requests


BASE_URL = "http://127.0.0.1:8000"
ASSET_PATH = Path(__file__).resolve().parents[1] / "test-assets" / "sample-garbage.jpg"


def request(method: str, path: str, **kwargs: Any) -> Any:
    response = requests.request(method, f"{BASE_URL}{path}", timeout=20, **kwargs)
    response.raise_for_status()
    return response.json()


def main() -> int:
    if not ASSET_PATH.exists():
        print(f"Missing sample image: {ASSET_PATH}", file=sys.stderr)
        return 1

    with ASSET_PATH.open("rb") as image:
        uploaded = request(
            "POST",
            "/api/uploads/images",
            files={"file": (ASSET_PATH.name, image, "image/jpeg")},
        )
    photo_url = uploaded["photoUrl"]
    print("Uploaded image:", photo_url)

    created = request(
        "POST",
        "/api/complaints",
        json={
            "originalText": "Garbage is blocking the drain near Madhapur Metro.",
            "normalizedEnglishText": "Garbage is blocking the drain near Madhapur Metro.",
            "originalLanguage": "en",
            "detectedLanguage": "en",
            "category": "SANITATION",
            "subcategory": "GARBAGE_BLOCKING_DRAIN",
            "department": "MULTI_DEPARTMENT",
            "priority": "HIGH",
            "latitude": 17.4483,
            "longitude": 78.3915,
            "landmark": "Near Madhapur Metro",
            "locality": "Madhapur",
            "photoUrl": photo_url,
            "analysisSource": "MANUAL",
            "requiresHumanVerification": True,
        },
    )
    reference_id = created["referenceId"]
    tracked = request("GET", f"/api/complaints/{reference_id}")
    if tracked["photoUrl"] != photo_url:
        print("Photo URL mismatch", file=sys.stderr)
        return 1

    print("Created complaint:", reference_id)
    print("Tracked photo URL matches uploaded URL.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
