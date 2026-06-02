from app.services.embedding_service import build_embedding_source_text, deterministic_embedding


def test_embedding_source_text_preserves_context():
    source = build_embedding_source_text(
        normalized_english_text="Garbage is blocking the drain near Kukatpally Metro.",
        category="SANITATION",
        landmark="Kukatpally Metro",
        locality="Kukatpally",
    )
    assert "Category: SANITATION" in source
    assert "Kukatpally Metro" in source
    assert "Locality: Kukatpally" in source


def test_deterministic_embedding_dimensions_and_norm():
    vector = deterministic_embedding("garbage drain kukatpally", 32)
    assert len(vector) == 32
    assert any(value != 0 for value in vector)
