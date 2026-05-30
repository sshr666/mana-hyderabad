from app.repositories.complaint_repository import get_hotspots, get_nearby_complaints
from app.models.complaint import ComplaintCategory
from app.schemas.complaint import ComplaintCreate
from app.services.complaint_service import create_complaint
from tests.conftest import requires_database


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
