
import pytest

from multilingual.translation.translator import (
    EnglishHindiTranslator,
    DemoTranslationProvider,
    HindiEnglishTranslator,
    translate
)
from multilingual.translation.language_detector import detect_language

DAY5_GLOSSARY = [
    {
        "term_id": "IP_001",
        "category": "Intellectual Property",
        "preferred_en": "Patent",
        "preferred_hindi": "पेटेंट",
        "aliases_en": ["patent"],
        "aliases_hi": ["पेटेन्ट"]
    },
    {
        "term_id": "IP_002",
        "category": "Intellectual Property",
        "preferred_en": "Prior Art",
        "preferred_hindi": "पूर्व कला",
        "aliases_en": ["prior art"],
        "aliases_hi": []
    },
    {
        "term_id": "TK_001",
        "category": "Traditional Knowledge",
        "preferred_en": "Traditional Knowledge",
        "preferred_hindi": "पारंपरिक ज्ञान",
        "aliases_en": ["traditional knowledge"],
        "aliases_hi": []
    },
    {
        "term_id": "AYU_001",
        "category": "Ayurveda",
        "preferred_en": "Ayurveda",
        "preferred_hindi": "आयुर्वेद",
        "aliases_en": ["ayurvedic"],
        "aliases_hi": []
    }
]




# ------------------------------------------------------------
# Mock glossary for testing
# ------------------------------------------------------------

class MockGlossary:

    TERMS = [
        {
            "matched_text": "Patent",
            "term_id": "PAT-001",
            "category": "Patent",
            "preferred_hi": "पेटेंट"
        },
        {
            "matched_text": "Prior Art",
            "term_id": "PAT-002",
            "category": "Patent",
            "preferred_hi": "पूर्व कला"
        },
        {
            "matched_text": "Ayurveda",
            "term_id": "AYU-001",
            "category": "Ayurveda",
            "preferred_hi": "आयुर्वेद"
        },
        {
            "matched_text": "Traditional Knowledge",
            "term_id": "TK-001",
            "category": "Traditional Knowledge",
            "preferred_hi": "पारंपरिक ज्ञान"
        },
        {
            "matched_text": "Agricultural Knowledge",
            "term_id": "AGR-001",
            "category": "Agriculture",
            "preferred_hi": "कृषि ज्ञान"
        }
    ]

    def find_terms(self, text):

        results = []

        for term in self.TERMS:

            if term["matched_text"].lower() in text.lower():
                results.append(term)

        return results


# ------------------------------------------------------------
# Fixture
# ------------------------------------------------------------

@pytest.fixture
def translator():

    glossary = MockGlossary()
    provider = DemoTranslationProvider()

    return EnglishHindiTranslator(
        glossary_engine=glossary,
        provider=provider
    )


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------

def test_patent_term_detection(translator):

    result = translator.translate(
        "This is a patent."
    )

    assert result["detected_terms"][0]["term_id"] == "PAT-001"


def test_patent_translation(translator):

    result = translator.translate(
        "This is a patent"
    )

    assert "पेटेंट" in result["final_translation"]


def test_traditional_knowledge_detection(translator):

    result = translator.translate(
        "Traditional Knowledge is important."
    )

    ids = [
        term["term_id"]
        for term in result["detected_terms"]
    ]

    assert "TK-001" in ids


def test_ayurveda_detection(translator):

    result = translator.translate(
        "Ayurveda uses traditional knowledge."
    )

    ids = [
        term["term_id"]
        for term in result["detected_terms"]
    ]

    assert "AYU-001" in ids


def test_empty_input(translator):

    with pytest.raises(ValueError):

        translator.translate("")


def test_non_string_input(translator):

    with pytest.raises(TypeError):

        translator.translate(123)


def test_validation(translator):

    result = translator.translate(
        "This is a patent"
    )

    assert result["validation"]["valid"] is True


def test_case_insensitive_detection(translator):

    result = translator.translate(
        "THIS IS A PATENT"
    )

    ids = [
        term["term_id"]
        for term in result["detected_terms"]
    ]

    assert "PAT-001" in ids

def test_day5_hindi_to_english():
    translator = HindiEnglishTranslator(
        DAY5_GLOSSARY
    )

    result = translator.translate(
        "पेटेंट क्या है?"
    )

    output = result["final_translation"]

    assert "Patent" in output
    assert "what is" in output

def test_day5_technical_hindi():
    translator = HindiEnglishTranslator(
        DAY5_GLOSSARY
    )

    result = translator.translate(
        "पूर्व कला खोजें"
    )

    output = result["final_translation"]

    assert "Prior Art" in output
    assert "search" in output

def test_day5_traditional_knowledge():
    translator = HindiEnglishTranslator(
        DAY5_GLOSSARY
    )

    result = translator.translate(
        "पारंपरिक ज्ञान की जानकारी चाहिए"
    )

    output = result["final_translation"]

    assert "Traditional Knowledge" in output
    assert "information" in output
    assert "need" in output

def test_day5_mixed_language_query():
    translator = HindiEnglishTranslator(
        DAY5_GLOSSARY
    )

    result = translator.translate(
        "पेटेंट application कैसे file करें?"
    )

    output = result["final_translation"]

    assert "Patent" in output
    assert "application" in output
    assert "file" in output
    assert "how" in output

def test_day5_detect_hindi():
    assert detect_language(
        "पेटेंट क्या है?"
    ) == "hi"


def test_day5_detect_english():
    assert detect_language(
        "What is a patent?"
    ) == "en"


def test_day5_detect_mixed():
    assert detect_language(
        "पेटेंट application कैसे file करें?"
    ) == "mixed"

def test_day5_auto_detection():
    translator = HindiEnglishTranslator(
        DAY5_GLOSSARY
    )

    text = "पेटेंट क्या है?"

    detected = detect_language(text)

    assert detected == "hi"

    result = translator.translate(text)

    assert "Patent" in result["final_translation"]

def test_day5_central_translate():
    result = translate(
        "पेटेंट क्या है?",
        source_language="hi",
        target_language="en",
        glossary_path="multilingual/glossary/glossary.json"
    )

    assert "Patent" in result