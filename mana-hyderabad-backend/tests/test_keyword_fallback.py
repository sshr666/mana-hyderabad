from app.schemas.analysis import ComplaintAnalysisRequest
from app.services.keyword_fallback import analyse_with_keyword_fallback


def test_garbage_blocking_drain_fallback():
    response = analyse_with_keyword_fallback(
        ComplaintAnalysisRequest(text="There is a lot of garbage near the school and it is blocking the drain."),
        "There is a lot of garbage near the school and it is blocking the drain.",
    )

    assert response.category == "SANITATION"
    assert response.department == "MULTI_DEPARTMENT"
    assert response.priority == "HIGH"
    assert "gps_location" in response.missing_fields


def test_robbery_defaults_to_other():
    response = analyse_with_keyword_fallback(
        ComplaintAnalysisRequest(text="There was a house robbery near Kondapur."),
        "There was a house robbery near Kondapur.",
    )

    assert response.category == "OTHER"
    assert response.department == "MANUAL_REVIEW"


def test_locality_is_preserved_in_fallback():
    response = analyse_with_keyword_fallback(
        ComplaintAnalysisRequest(text="There is a large pothole near Charminar"),
        "There is a large pothole near Charminar",
    )

    assert response.category == "ROADS"
    assert response.location_text == "Charminar"
