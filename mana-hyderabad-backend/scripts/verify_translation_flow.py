import json
from typing import Any

import requests

BASE_URL = "http://127.0.0.1:8000"

SAMPLES = [
    ("English", "Garbage has accumulated near Madhapur Metro.", "en"),
    ("Telugu", "మాధాపూర్ మెట్రో దగ్గర చెత్త పేరుకుపోయింది", "te"),
    ("Hindi", "गाचीबोवली सिग्नल के पास पानी जमा है", "hi"),
    ("Urdu", "چارمینار کے پاس سڑک پر گڑھا ہے", "ur"),
    ("Mixed Telugu-English", "Madhapur metro దగ్గర garbage dump అయింది", "te"),
    ("Mixed Hindi-English", "Road pe bahut waterlogging hai near Gachibowli signal", "hi"),
    ("Romanised Telugu", "Kondapur lo drain block ayindi", "te"),
]


def post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def get(path: str) -> dict[str, Any]:
    response = requests.get(f"{BASE_URL}{path}", timeout=20)
    response.raise_for_status()
    return response.json()


def main() -> None:
    print("Verifying translation flow...")
    for label, text, language in SAMPLES:
        detected = post("/api/translation/detect-language", {"text": text})
        translated = post(
            "/api/translation/translate",
            {"text": text, "sourceLanguage": language, "targetLanguage": "en"},
        )
        analysis = post(
            "/api/complaints/analyse",
            {
                "text": text,
                "language": language,
                "photoUrl": None,
                "latitude": 17.4483,
                "longitude": 78.3915,
                "landmark": "Near Madhapur Metro",
            },
        )
        print(
            json.dumps(
                {
                    "sample": label,
                    "detected": detected["detectedLanguage"],
                    "provider": translated["provider"],
                    "normalized": analysis["normalizedEnglishText"],
                    "citizenReply": analysis.get("citizenReply"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    sample_text = "Madhapur metro దగ్గర garbage dump అయింది"
    analysis = post(
        "/api/complaints/analyse",
        {"text": sample_text, "language": "te", "photoUrl": None, "latitude": 17.4483, "longitude": 78.3915},
    )
    created = post(
        "/api/complaints",
        {
            "originalText": sample_text,
            "normalizedEnglishText": analysis["normalizedEnglishText"],
            "originalLanguage": "te",
            "detectedLanguage": analysis["detectedLanguage"],
            "category": analysis["category"],
            "subcategory": analysis["subcategory"],
            "department": analysis["department"],
            "priority": analysis["priority"],
            "latitude": 17.4483,
            "longitude": 78.3915,
            "landmark": "Near Madhapur Metro",
            "locality": "Madhapur",
            "analysisSource": analysis["analysisSource"],
            "requiresHumanVerification": True,
            "reasoningSummary": analysis["reasoningSummary"],
        },
    )
    retrieved = get(f"/api/complaints/{created['referenceId']}")
    assert retrieved["originalText"] == sample_text
    assert retrieved["normalizedEnglishText"]
    print(f"Stored translated complaint: {created['referenceId']}")
    print("Translation flow verification completed.")


if __name__ == "__main__":
    main()
