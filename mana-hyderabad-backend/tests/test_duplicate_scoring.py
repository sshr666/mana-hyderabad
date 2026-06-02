from app.models.complaint import DuplicateConfidence
from app.services.duplicate_detection_service import calculate_duplicate_score, confidence_label, cosine_similarity


def test_duplicate_score_high_with_close_semantic_match():
    score = calculate_duplicate_score(
        semantic_similarity=0.91,
        distance_meters=42,
        radius_meters=200,
        time_difference_hours=3,
        time_window_hours=72,
        category_match=True,
    )
    label = confidence_label(
        duplicate_score=score,
        semantic_similarity=0.91,
        min_similarity=0.78,
        high_similarity=0.88,
    )
    assert score >= 0.85
    assert label == DuplicateConfidence.HIGH


def test_low_semantic_similarity_not_promoted():
    score = calculate_duplicate_score(
        semantic_similarity=0.40,
        distance_meters=10,
        radius_meters=200,
        time_difference_hours=1,
        time_window_hours=72,
        category_match=True,
    )
    label = confidence_label(
        duplicate_score=score,
        semantic_similarity=0.40,
        min_similarity=0.78,
        high_similarity=0.88,
    )
    assert label == DuplicateConfidence.LOW


def test_postgis_only_candidate_can_still_be_medium():
    score = calculate_duplicate_score(
        semantic_similarity=None,
        distance_meters=30,
        radius_meters=200,
        time_difference_hours=2,
        time_window_hours=72,
        category_match=True,
    )
    assert score >= 0.65


def test_cosine_similarity_handles_invalid_vectors():
    assert cosine_similarity(None, [1.0]) is None
    assert cosine_similarity([1.0], [1.0, 0.0]) is None
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
