from __future__ import annotations

import json
from pathlib import Path
import sys

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


BASE_URL = "http://127.0.0.1:8000"


def post_complaint(text: str, latitude: float, longitude: float) -> dict:
    payload = {
        "originalText": text,
        "normalizedEnglishText": text,
        "originalLanguage": "en",
        "detectedLanguage": "en",
        "category": "SANITATION",
        "subcategory": "GARBAGE_BLOCKING_DRAIN",
        "department": "MULTI_DEPARTMENT",
        "priority": "HIGH",
        "latitude": latitude,
        "longitude": longitude,
        "landmark": "Near Kukatpally Metro",
        "locality": "Kukatpally",
        "analysisSource": "MANUAL",
        "requiresHumanVerification": True,
    }
    response = requests.post(f"{BASE_URL}/api/complaints", json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def main() -> None:
    health = requests.get(f"{BASE_URL}/api/health", timeout=10)
    health.raise_for_status()
    first = post_complaint("Garbage is blocking the drain near Kukatpally Metro.", 17.4933, 78.3915)
    second = post_complaint("Waste piled beside drainage line near Kukatpally station.", 17.49355, 78.39175)
    suggestions = requests.post(
        f"{BASE_URL}/api/admin/complaints/{second['referenceId']}/run-duplicate-check",
        timeout=20,
    )
    suggestions.raise_for_status()
    items = suggestions.json()
    print(json.dumps({"first": first["referenceId"], "second": second["referenceId"], "suggestions": items}, indent=2))
    if items:
        confirm = requests.post(
            f"{BASE_URL}/api/admin/duplicate-suggestions/{items[0]['suggestionId']}/confirm",
            json={"reviewedBy": "admin", "reviewNote": "Same sanitation issue near Kukatpally Metro."},
            timeout=20,
        )
        confirm.raise_for_status()
        print(json.dumps(confirm.json(), indent=2))
    analytics = requests.get(f"{BASE_URL}/api/admin/analytics", timeout=20)
    analytics.raise_for_status()
    print(json.dumps({"analytics": analytics.json()}, indent=2))


if __name__ == "__main__":
    main()
