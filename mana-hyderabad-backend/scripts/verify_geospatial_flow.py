import sys
from typing import Any

import requests


BASE_URL = "http://127.0.0.1:8000"


def request(method: str, path: str, **kwargs: Any) -> Any:
    response = requests.request(method, f"{BASE_URL}{path}", timeout=15, **kwargs)
    response.raise_for_status()
    return response.json()


def main() -> int:
    payload = {
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
        "analysisSource": "MANUAL",
        "requiresHumanVerification": True,
    }
    created = request("POST", "/api/complaints", json=payload)
    reference_id = created["referenceId"]
    tracked = request("GET", f"/api/complaints/{reference_id}")
    assert tracked["latitude"] == payload["latitude"]
    assert tracked["longitude"] == payload["longitude"]

    map_points = request("GET", "/api/admin/map-points", params={"category": "SANITATION"})
    assert any(point["referenceId"] == reference_id for point in map_points)

    nearby = request("GET", "/api/admin/nearby-complaints", params={"latitude": 17.4483, "longitude": 78.3915, "radius_meters": 200})
    assert any(item["referenceId"] == reference_id and "distanceMeters" in item for item in nearby)

    hotspots = request("GET", "/api/admin/hotspots", params={"radius_meters": 300, "min_complaints": 3})
    analytics = request("GET", "/api/admin/analytics")
    assert "complaintsByLocality" in analytics
    assert "hotspots" in analytics

    print("Created complaint:", reference_id)
    print("Map points:", len(map_points))
    print("Nearby sample:", nearby[:2])
    print("Hotspot sample:", hotspots[:2])
    print("Geospatial verification passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, requests.RequestException) as exc:
        print(f"Geospatial verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
