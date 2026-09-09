from multilingual.glossary.glossary_anchor import load_glossary
from multilingual.translation.translator import (
    EnglishHindiTranslator,
    DemoTranslationProvider
)


GLOSSARY_PATH = "multilingual/glossary/glossary.json"


def test_real_glossary_loads():

    glossary = load_glossary(GLOSSARY_PATH)

    assert isinstance(glossary, list)
    assert len(glossary) > 0


def test_real_glossary_detects_terms():

    glossary = load_glossary(GLOSSARY_PATH)

    translator = EnglishHindiTranslator(
        glossary_engine=glossary,
        provider=DemoTranslationProvider()
    )

    result = translator.translate(
        "Patent protection is important."
    )

    assert isinstance(
        result["detected_terms"],
        list
    )