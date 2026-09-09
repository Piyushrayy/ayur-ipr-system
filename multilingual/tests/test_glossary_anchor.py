import json

import pytest

from multilingual.glossary.glossary_anchor import (
    load_glossary,
    normalize_term,
    find_terms,
    get_translation,
    create_anchors,
)


@pytest.fixture
def glossary(tmp_path):
    data = {
        "terms": [
            {
                "term_id": "PAT001",
                "category": "Patent",
                "preferred_english": "Patent",
                "preferred_hindi": "पेटेंट",
                "aliases": [
                    "patent",
                    "patents",
                    "patent protection"
                ],
                 "aliases_hi": [
                   "पेटेन्ट"
                ]
            },
            {
                "term_id": "PAT002",
                "category": "Patent",
                "preferred_english": "Prior Art",
                "preferred_hindi": "पूर्व कला",
                "aliases": [
                    "prior art",
                    "prior-art",
                    "previous art"
                ],  
                "aliases_hi": [
                 "पिछली कला"
                ]
            },
            {
                "term_id": "AYU001",
                "category": "Ayurveda",
                "preferred_english": "Ayurveda",
                "preferred_hindi": "आयुर्वेद",
                "aliases": [
                    "ayurveda",
                    "ayurvedic"
                ],
                 "aliases_hi": [
                    "आयुर्वेदिक"
                ]
            },
            {
                "term_id": "TK001",
                "category": "Traditional Knowledge",
                "preferred_english": "Traditional Knowledge",
                "preferred_hindi": "पारंपरिक ज्ञान",
                "aliases": [
                    "traditional knowledge",
                    "traditional know-how",
                    "indigenous knowledge"
                ],
                      "aliases_hi": [
                     "परंपरागत ज्ञान"
                ]
            }
        ]
    }

    glossary_path = tmp_path / "glossary.json"

    with glossary_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return load_glossary(glossary_path)


def test_load_glossary(glossary):
    assert len(glossary) == 4
    assert glossary[0]["term_id"] == "PAT001"


def test_normalize_term():
    assert normalize_term("  PATENT  ") == "patent"
    assert normalize_term("Prior-Art") == "prior art"
    assert normalize_term(
        "Traditional   Knowledge"
    ) == "traditional knowledge"

    
    


def test_case_insensitive_matching(glossary):

    text = "PATENT applications are important."

    matches = find_terms(text, glossary)

    assert len(matches) == 1
    assert matches[0]["term_id"] == "PAT001"
    assert matches[0]["matched_text"] == "PATENT"


def test_patent_alias(glossary):

    text = "The company filed for patent protection."

    matches = find_terms(text, glossary)

    assert any(
        match["term_id"] == "PAT001"
        for match in matches
    )


def test_prior_art(glossary):

    text = "The examiner found prior-art."

    matches = find_terms(text, glossary)

    assert len(matches) == 1
    assert matches[0]["term_id"] == "PAT002"
    assert matches[0]["preferred_hindi"] == "पूर्व कला"


def test_ayurveda(glossary):

    text = "Ayurvedic knowledge is valuable."

    matches = find_terms(text, glossary)

    assert len(matches) == 1
    assert matches[0]["term_id"] == "AYU001"
    assert matches[0]["category"] == "Ayurveda"


def test_traditional_knowledge(glossary):

    text = "India has extensive traditional knowledge."

    matches = find_terms(text, glossary)

    assert len(matches) == 1

    assert matches[0]["term_id"] == "TK001"

    assert (
        matches[0]["preferred_english"]
        == "Traditional Knowledge"
    )

    assert (
        matches[0]["preferred_hindi"]
        == "पारंपरिक ज्ञान"
    )


def test_indigenous_knowledge_alias(glossary):

    text = "Indigenous knowledge must be documented."

    matches = find_terms(text, glossary)

    assert len(matches) == 1
    assert matches[0]["term_id"] == "TK001"


def test_get_hindi_translation(glossary):

    result = get_translation(
        "PAT001",
        glossary,
        "hindi"
    )

    assert result == "पेटेंट"


def test_get_english_translation(glossary):

    result = get_translation(
        "PAT002",
        glossary,
        "english"
    )

    assert result == "Prior Art"


def test_unknown_term(glossary):

    result = get_translation(
        "UNKNOWN",
        glossary,
        "hindi"
    )

    assert result is None


def test_create_anchors(glossary):

    text = """
    Patent law considers prior art.
    Ayurveda contains traditional knowledge.
    """

    anchors = create_anchors(
        text,
        glossary
    )

    term_ids = {
        anchor["term_id"]
        for anchor in anchors
    }

    assert "PAT001" in term_ids
    assert "PAT002" in term_ids
    assert "AYU001" in term_ids
    assert "TK001" in term_ids


def test_no_partial_word_match(glossary):

    text = "The article discusses technology."

    matches = find_terms(text, glossary)

    patent_matches = [
        match
        for match in matches
        if match["term_id"] == "PAT001"
    ]

    assert patent_matches == []

def test_hindi_patent_detection(glossary):
    

    matches = find_terms(
        "पेटेंट क्या है?",
        glossary
    )

    assert len(matches) >= 1
    assert matches[0]["matched_text"] == "पेटेंट"
    assert matches[0]["preferred_english"] == "Patent"


def test_hindi_prior_art_detection(glossary):
    

    matches = find_terms(
        "पूर्व कला खोजें",
        glossary
    )

    assert len(matches) >= 1
    assert matches[0]["matched_text"] == "पूर्व कला"
    assert matches[0]["preferred_english"] == "Prior Art"


def test_hindi_traditional_knowledge_detection(glossary):
    

    matches = find_terms(
        "पारंपरिक ज्ञान महत्वपूर्ण है",
        glossary
    )

    assert len(matches) >= 1
    assert matches[0]["matched_text"] == "पारंपरिक ज्ञान"
    assert matches[0]["preferred_english"] == "Traditional Knowledge"

