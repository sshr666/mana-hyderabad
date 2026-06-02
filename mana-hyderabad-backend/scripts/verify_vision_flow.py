from __future__ import annotations

import json

import requests


BASE_URL = "http://127.0.0.1:8000"
SAMPLE_IMAGE_URL = "https://res.cloudinary.com/demo/image/upload/sample.jpg"


def main() -> None:
    health = requests.get(f"{BASE_URL}/api/vision/health", timeout=10)
    health.raise_for_status()
    print(json.dumps({"health": health.json()}, indent=2))

    direct = requests.post(f"{BASE_URL}/api/vision/analyse", json={"photoUrl": SAMPLE_IMAGE_URL}, timeout=30)
    direct.raise_for_status()
    print(json.dumps({"directAnalysis": direct.json()}, indent=2))

    complaint_payload = {
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
        "photoUrl": SAMPLE_IMAGE_URL,
        "analysisSource": "MANUAL",
        "requiresHumanVerification": True,
    }
    complaint = requests.post(f"{BASE_URL}/api/complaints", json=complaint_payload, timeout=20)
    complaint.raise_for_status()
    reference_id = complaint.json()["referenceId"]

    run = requests.post(f"{BASE_URL}/api/admin/complaints/{reference_id}/run-vision-analysis", timeout=30)
    run.raise_for_status()
    stored = requests.get(f"{BASE_URL}/api/admin/complaints/{reference_id}/vision-analysis", timeout=20)
    stored.raise_for_status()
    print(json.dumps({"referenceId": reference_id, "vision": stored.json()}, indent=2))


if __name__ == "__main__":
    main()
