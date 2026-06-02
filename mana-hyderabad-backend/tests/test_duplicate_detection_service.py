from app.models.complaint import ComplaintCategory
from app.schemas.complaint import ComplaintCreate
from app.services.complaint_service import create_complaint
from app.services.duplicate_detection_service import detect_duplicate_candidates
from tests.conftest import requires_database


@requires_database
def test_duplicate_detection_skips_missing_coordinates(db_session):
    complaint = create_complaint(
        db_session,
        ComplaintCreate(
            originalText="Garbage near Kukatpally Metro",
            normalizedEnglishText="Garbage near Kukatpally Metro",
            category=ComplaintCategory.SANITATION,
            priority="MEDIUM",
            landmark="Kukatpally Metro",
        ),
    )
    assert detect_duplicate_candidates(db_session, complaint.id) == []
