from app.services.language_detection_service import detect_language


def test_detects_english():
    result = detect_language("Garbage has accumulated near Madhapur Metro.")

    assert result.detected_language == "en"
    assert result.is_mixed_language is False


def test_detects_telugu_script():
    result = detect_language("మాధాపూర్ మెట్రో దగ్గర చెత్త పేరుకుపోయింది")

    assert "te" in result.detected_language
    assert "Telugu" in result.detected_scripts


def test_detects_hindi_script():
    result = detect_language("गाचीबोवली सिग्नल के पास पानी जमा है")

    assert "hi" in result.detected_language
    assert "Devanagari" in result.detected_scripts


def test_detects_urdu_script():
    result = detect_language("چارمینار کے پاس سڑک پر گڑھا ہے")

    assert "ur" in result.detected_language
    assert "Perso-Arabic" in result.detected_scripts


def test_detects_mixed_telugu_english():
    result = detect_language("Madhapur metro దగ్గర garbage dump అయింది")

    assert result.detected_language == "te-en"
    assert result.is_mixed_language is True


def test_detects_romanised_telugu():
    result = detect_language("Kondapur lo drain block ayindi")

    assert result.detected_language in {"te-latn", "te-latn-en"}
    assert result.is_mixed_language is True
