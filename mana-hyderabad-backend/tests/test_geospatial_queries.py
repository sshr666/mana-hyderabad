from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.repositories.complaint_repository import count_by_locality, get_hotspots, get_map_points, get_nearby_complaints
from app.models.complaint import ComplaintCategory
from app.schemas.complaint import ComplaintCreate
from app.services.complaint_service import create_complaint
from tests.conftest import requires_database


client = TestClient(app)


def test_invalid_coordinates_rejected_by_schema():
    for payload in [
        {"originalText": "Invalid latitude", "category": "SANITATION", "priority": "MEDIUM", "latitude": 91, "longitude": 78.39},
        {"originalText": "Invalid longitude", "category": "SANITATION", "priority": "MEDIUM", "latitude": 17.44, "longitude": 181},
    ]:
        with pytest.raises(Exception):
            ComplaintCreate(**payload)


def test_radius_greater_than_max_rejected():
    response = client.get("/api/admin/nearby-complaints?latitude=17.44&longitude=78.39&radius_meters=5001")
    assert response.status_code == 422


def test_null_coordinates_allowed_by_schema():
    payload = ComplaintCreate(originalText="Landmark only complaint", category="OTHER", priority="LOW", landmark="Near Ameerpet Metro")
    assert payload.latitude is None
    assert payload.longitude is None


@requires_database
def test_radius_search_returns_nearby_sorted_and_filters_category(db_session):
    near = ComplaintCreate(
        originalText="Garbage near Madhapur Metro",
        category="SANITATION",
        priority="MEDIUM",
        latitude=17.4483,
        longitude=78.3915,
        locality="Madhapur",
    )
    far = ComplaintCreate(
        originalText="Garbage near Charminar",
        category="SANITATION",
        priority="MEDIUM",
        latitude=17.3616,
        longitude=78.4747,
        locality="Charminar",
    )
    road = ComplaintCreate(
        originalText="Pothole near Madhapur Metro",
        category="ROADS",
        priority="HIGH",
        latitude=17.4484,
        longitude=78.3916,
        locality="Madhapur",
    )
    create_complaint(db_session, near)
    create_complaint(db_session, far)
    create_complaint(db_session, road)

    results = get_nearby_complaints(db_session, latitude=17.4483, longitude=78.3915, radius_meters=200)
    filtered = get_nearby_complaints(
        db_session,
        latitude=17.4483,
        longitude=78.3915,
        radius_meters=200,
        category=ComplaintCategory.SANITATION,
    )

    assert len(results) >= 2
    assert all(results[index][1] <= results[index + 1][1] for index in range(len(results) - 1))
    assert all(row[0].category == ComplaintCategory.SANITATION for row in filtered)


@requires_database
def test_map_points_exclude_null_coordinates_and_filter(db_session):
    create_complaint(db_session, ComplaintCreate(originalText="No coords", category="OTHER", priority="LOW", landmark="Near Ameerpet Metro"))
    create_complaint(db_session, ComplaintCreate(originalText="Pothole", category="ROADS", priority="HIGH", latitude=17.45, longitude=78.38, locality="Hitech City"))
    create_complaint(db_session, ComplaintCreate(originalText="Garbage", category="SANITATION", priority="MEDIUM", latitude=17.44, longitude=78.39, locality="Madhapur"))

    points = get_map_points(db_session)
    road_points = get_map_points(db_session, category=ComplaintCategory.ROADS)

    assert all(point.latitude is not None and point.longitude is not None for point in points)
    assert all(point.category == ComplaintCategory.ROADS for point in road_points)


@requires_database
def test_locality_count_and_hotspot_threshold(db_session):
    for index in range(2):
        create_complaint(db_session, ComplaintCreate(originalText=f"Below threshold {index}", category="DRAINAGE", priority="MEDIUM", latitude=17.44 + index * 0.0001, longitude=78.35, locality="Gachibowli"))
    counts = count_by_locality(db_session)
    below = get_hotspots(db_session, radius_meters=300, min_complaints=3, category=ComplaintCategory.DRAINAGE)

    assert any(item["locality"] == "Gachibowli" for item in counts)
    assert not any(item["locality"] == "Gachibowli" and item["category"] == ComplaintCategory.DRAINAGE for item in below)


@requires_database
def test_hotspots_group_by_locality_and_category(db_session):
    for index in range(3):
        create_complaint(
            db_session,
            ComplaintCreate(
                originalText=f"Garbage hotspot {index}",
                category="SANITATION",
                priority="MEDIUM",
                latitude=17.4483 + (index * 0.0001),
                longitude=78.3915,
                locality="Madhapur",
            ),
        )

    hotspots = get_hotspots(db_session, radius_meters=300, min_complaints=3)
    assert any(item["locality"] == "Madhapur" and item["category"] == ComplaintCategory.SANITATION for item in hotspots)
