import pytest
from sqlalchemy import text

from app.models.complaint import ComplaintCategory
from app.schemas.complaint import ComplaintCreate
from app.services.complaint_service import create_complaint, generate_reference_id, get_complaint_by_reference
from tests.conftest import requires_database


@requires_database
def test_database_connection_and_postgis(db_session):
    version = db_session.scalar(text("SELECT PostGIS_Version()"))
    assert version


@requires_database
def test_create_complaint_generates_reference_and_persists(db_session):
    payload = ComplaintCreate(
        originalText="Garbage is blocking the drain near Madhapur Metro.",
        normalizedEnglishText="Garbage is blocking the drain near Madhapur Metro.",
        originalLanguage="en",
        detectedLanguage="en",
        category="SANITATION",
        subcategory="GARBAGE_BLOCKING_DRAIN",
        department="MULTI_DEPARTMENT",
        priority="HIGH",
        latitude=17.4483,
        longitude=78.3915,
        landmark="Near Madhapur Metro",
        locality="Madhapur",
        wardNumber=107,
    )
    complaint = create_complaint(db_session, payload)
    found = get_complaint_by_reference(db_session, complaint.reference_id)

    assert complaint.reference_id.startswith("HYD-SAN-")
    assert found.reference_id == complaint.reference_id
    assert found.location is not None


@requires_database
def test_reference_generation_uses_category_prefix(db_session):
    reference_id = generate_reference_id(db_session, ComplaintCategory.WATER_SUPPLY)
    assert reference_id.startswith("HYD-WSP-")


@pytest.mark.parametrize(
    ("field", "value"),
    [("latitude", 99), ("longitude", 190), ("category", "NOT_A_CATEGORY"), ("priority", "NOT_A_PRIORITY")],
)
def test_validation_rejects_invalid_payloads(field, value):
    payload = {
        "originalText": "Invalid test complaint",
        "category": "SANITATION",
        "priority": "MEDIUM",
        "latitude": 17.44,
        "longitude": 78.39,
    }
    payload[field] = value

    with pytest.raises(Exception):
        ComplaintCreate(**payload)
