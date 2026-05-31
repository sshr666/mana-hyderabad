import re
from dataclasses import dataclass


HYDERABAD_TERMS = [
    "Hyderabad",
    "Madhapur Metro",
    "Madhapur metro",
    "Madhapur",
    "Gachibowli signal",
    "Gachibowli Signal",
    "Gachibowli",
    "Kondapur RTO office",
    "Kondapur",
    "Kukatpally",
    "Ameerpet",
    "Jubilee Hills",
    "Banjara Hills",
    "Charminar",
    "Begumpet",
    "Secunderabad",
    "Hitech City",
    "Mehdipatnam",
    "Tolichowki",
    "Miyapur",
    "Tarnaka",
    "Botanical Garden",
    "چارمینار",
    "మాధాపూర్ మెట్రో",
    "గాచిబౌలి సిగ్నల్",
    "माधापुर मेट्रो",
    "गाचीबोवली सिग्नल",
]

LOCALITY_TRANSLITERATIONS = {
    "چارمینار": "Charminar",
    "مادھاپور": "Madhapur",
    "گچی باؤلی": "Gachibowli",
    "మాధాపూర్ మెట్రో": "Madhapur Metro",
    "గాచిబౌలి సిగ్నల్": "Gachibowli signal",
    "गाचीबोवली सिग्नल": "Gachibowli signal",
    "माधापुर मेट्रो": "Madhapur Metro",
}


@dataclass(frozen=True)
class ProtectedText:
    text: str
    placeholders: dict[str, str]
    preserved_terms: list[str]


def protect_locality_terms(text: str, preserve_terms: list[str] | None = None) -> ProtectedText:
    terms = sorted(set([*(preserve_terms or []), *HYDERABAD_TERMS]), key=len, reverse=True)
    protected = text
    placeholders: dict[str, str] = {}
    preserved_terms: list[str] = []
    placeholder_index = 0
    for term in terms:
        if not term:
            continue
        pattern = re.compile(re.escape(term), flags=re.IGNORECASE if term.isascii() else 0)
        if not pattern.search(protected):
            continue
        placeholder = f"__PLACE_{placeholder_index}__"
        match = pattern.search(protected)
        if not match:
            continue
        original = match.group(0)
        restored = LOCALITY_TRANSLITERATIONS.get(original, _normalize_term_case(original))
        protected = pattern.sub(placeholder, protected)
        placeholders[placeholder] = restored
        preserved_terms.append(restored)
        placeholder_index += 1
    return ProtectedText(text=protected, placeholders=placeholders, preserved_terms=preserved_terms)


def restore_locality_terms(text: str, protected: ProtectedText) -> str:
    restored = text
    for placeholder, term in protected.placeholders.items():
        restored = restored.replace(placeholder, term)
    return restored


def extract_locality_terms(text: str) -> list[str]:
    return protect_locality_terms(text).preserved_terms


def _normalize_term_case(term: str) -> str:
    lower = term.lower()
    for known in HYDERABAD_TERMS:
        if known.lower() == lower and known.isascii():
            return known
    return term
