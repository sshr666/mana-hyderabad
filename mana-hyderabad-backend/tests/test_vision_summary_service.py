from app.schemas.vision import DetectedObject
from app.services.vision_summary_service import build_admin_summary, build_citizen_message


def test_garbage_summary_is_cautious():
    message = build_citizen_message([DetectedObject(label="garbage_heap", confidence=0.84)])
    assert "appears to show garbage accumulation" in message
    assert "Field verification is required" in message
    assert "confirmed" not in message.lower()


def test_multiple_detection_summary_mentions_both():
    objects = [
        DetectedObject(label="garbage_heap", confidence=0.84),
        DetectedObject(label="blocked_drain", confidence=0.71),
    ]
    assert "garbage accumulation and a possible drain blockage" in build_citizen_message(objects)
    admin = build_admin_summary(objects)
    assert "Garbage heap: 84%" in admin
    assert "Possible blocked drain: 71%" in admin
    assert "verify" in admin.lower()


def test_no_detections_safe_message():
    message = build_citizen_message([])
    assert "No supported issue type" in message
    assert "Field verification" in message
