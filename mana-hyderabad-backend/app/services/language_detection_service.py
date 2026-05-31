from app.schemas.translation import DetectLanguageResponse


TELUGU_RANGE = ("\u0c00", "\u0c7f")
DEVANAGARI_RANGE = ("\u0900", "\u097f")
PERSO_ARABIC_RANGE = ("\u0600", "\u06ff")

ROMANISED_TELUGU_HINTS = {
    "lo",
    "daggara",
    "ayindi",
    "undi",
    "chaala",
    "kuda",
    "mettu",
}
ROMANISED_HINDI_HINTS = {
    "pe",
    "paas",
    "bahut",
    "hai",
    "kaam",
    "nahi",
    "ke",
    "gaya",
}
URDU_HINTS = {"چارمینار", "سڑک", "گڑھا", "پاس", "پانی"}
ENGLISH_CIVIC_HINTS = {
    "garbage",
    "drain",
    "waterlogging",
    "pothole",
    "street",
    "light",
    "signal",
    "road",
}


def detect_language(text: str, selected_language: str | None = None) -> DetectLanguageResponse:
    stripped = text.strip()
    scripts = detect_scripts(stripped)
    lower_tokens = set(stripped.lower().replace(".", " ").replace(",", " ").split())

    language_parts: list[str] = []
    if "Telugu" in scripts:
        language_parts.append("te")
    if "Devanagari" in scripts:
        language_parts.append("hi")
    if "Perso-Arabic" in scripts:
        language_parts.append("ur")

    romanised = False
    has_latin = "Latin" in scripts
    if has_latin and not any(script in scripts for script in ["Telugu", "Devanagari", "Perso-Arabic"]):
        if ROMANISED_TELUGU_HINTS.intersection(lower_tokens):
            language_parts.append("te-latn")
            romanised = True
        elif ROMANISED_HINDI_HINTS.intersection(lower_tokens):
            language_parts.append("hi-en")
            romanised = True
    if has_latin and ENGLISH_CIVIC_HINTS.intersection(lower_tokens):
        if not romanised:
            language_parts.append("en")

    if not language_parts and selected_language:
        language_parts.append(selected_language)
    if not language_parts and has_latin:
        language_parts.append("en")
    if not language_parts:
        language_parts.append("unknown")

    detected = _dedupe_language_parts(language_parts)
    is_mixed = "-" in detected or romanised or len(set(detected.split("-"))) > 1
    confidence = 0.9 if detected in {"en", "te", "hi", "ur"} else 0.78 if detected != "unknown" else 0.35
    return DetectLanguageResponse(
        detectedLanguage=detected,
        confidence=confidence,
        isMixedLanguage=is_mixed,
        detectedScripts=scripts,
        analysisSource="RULES",
    )


def detect_scripts(text: str) -> list[str]:
    scripts: list[str] = []
    if any(_in_range(char, TELUGU_RANGE) for char in text):
        scripts.append("Telugu")
    if any(_in_range(char, DEVANAGARI_RANGE) for char in text):
        scripts.append("Devanagari")
    if any(_in_range(char, PERSO_ARABIC_RANGE) for char in text):
        scripts.append("Perso-Arabic")
    if any(("A" <= char <= "Z") or ("a" <= char <= "z") for char in text):
        scripts.append("Latin")
    return scripts or ["Unknown"]


def _in_range(char: str, unicode_range: tuple[str, str]) -> bool:
    return unicode_range[0] <= char <= unicode_range[1]


def _dedupe_language_parts(parts: list[str]) -> str:
    ordered: list[str] = []
    for part in parts:
        if part not in ordered:
            ordered.append(part)
    if ordered == ["te", "en"]:
        return "te-en"
    if ordered == ["hi", "en"]:
        return "hi-en"
    if ordered == ["ur", "en"]:
        return "ur-en"
    return "-".join(ordered)
