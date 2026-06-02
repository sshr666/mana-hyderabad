from app.models.complaint import VisionStatus
from app.schemas.vision import BoundingBox, DetectedObject
from app.services.vision_analysis_service import not_configured_response, parse_yolo_results


def test_bounding_box_validation():
    box = BoundingBox(xMin=1, yMin=2, xMax=3, yMax=4)
    assert box.x_max == 3


def test_not_configured_response_is_safe():
    response = not_configured_response()
    assert response.status == VisionStatus.NOT_CONFIGURED
    assert response.requires_human_verification is True
    assert "unavailable" in response.citizen_message


def test_detected_object_confidence_validation():
    item = DetectedObject(label="pothole", confidence=0.72)
    assert item.label == "pothole"
