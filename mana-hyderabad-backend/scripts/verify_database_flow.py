import json
import sys
from typing import Any

import requests


BASE_URL = "http://127.0.0.1:8000"


def request(method: str, path: str, **kwargs: Any) -> Any:
    response = requests.request(method, f"{BASE_URL}{path}", timeout=10, **kwargs)
    response.raise_for_status()
    if response.content:
        return response.json()
    return None


def main() -> int:
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
        "requiresHumanVerification": True,
        "analysisSource": "MANUAL",
    }

    print("1. Health:", request("GET", "/api/health"))

    created = request("POST", "/api/complaints", json=complaint_payload)
    reference_id = created["referenceId"]
    print("2. Created reference:", reference_id)

    tracked = request("GET", f"/api/complaints/{reference_id}")
    print("3. Tracked status:", tracked["status"])

    updated = request("PATCH", f"/api/admin/complaints/{reference_id}", json={"status": "UNDER_REVIEW"})
    print("4. Updated status:", updated["status"])

    complaints = request("GET", "/api/admin/complaints", params={"page_size": 5})
    print("5. Admin complaints:", complaints["total"])

    map_points = request("GET", "/api/admin/map-points")
    print("6. Map points:", len(map_points))

    nearby = request(
        "GET",
        "/api/admin/nearby-complaints",
        params={"latitude": 17.4483, "longitude": 78.3915, "radius_meters": 200},
    )
    print("7. Nearby sample:", json.dumps(nearby[:2], indent=2))

    hotspots = request("GET", "/api/admin/hotspots", params={"radius_meters": 300, "min_complaints": 3})
    print("8. Hotspot sample:", json.dumps(hotspots[:2], indent=2))

    analytics = request("GET", "/api/admin/analytics")
    print("9. Analytics keys:", sorted(analytics.keys()))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
