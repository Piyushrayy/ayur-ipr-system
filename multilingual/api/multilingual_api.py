from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from multilingual.translation.translator import translate
from multilingual.translation.language_detector import detect_language

from multilingual.glossary.glossary_anchor import (
    load_glossary,
    find_terms
)

from multilingual.translation.query_screening import (
    screen_query
)


app = FastAPI(
    title="HERBAL_ROOTS Multilingual API",
    version="1.0.0"
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GLOSSARY_PATH = (
    PROJECT_ROOT
    / "multilingual"
    / "glossary"
    / "glossary.json"
)

class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Text to process."
    )


class TranslateRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Text to translate."
    )

    source_language: str = Field(
        default="auto",
        description="Source language: en, hi, mixed, or auto."
    )

    target_language: str = Field(
        default="en",
        description="Target language: en or hi."
    )


class ValidateTranslationRequest(BaseModel):
    original_text: str = Field(
        ...,
        min_length=1
    )

    translated_text: str = Field(
        ...,
        min_length=1
    )

    source_language: str = Field(
        default="auto"
    )

    target_language: str = Field(
        default="en"
    )

class LanguageResponse(BaseModel):
    text: str
    detected_language: str


class TermResponse(BaseModel):
    matched_text: Optional[str] = None
    term_id: Optional[str] = None
    category: Optional[str] = None
    preferred_english: Optional[str] = None
    preferred_hindi: Optional[str] = None


class ExtractTermsResponse(BaseModel):
    text: str
    detected_language: str
    matched_terms: List[TermResponse]


class ScreeningResponse(BaseModel):
    valid: bool
    grammar_ok: bool
    issues: List[str]
    warnings: List[str]


class TranslateResponse(BaseModel):
    original_text: str
    detected_language: str
    source_language: str
    target_language: str
    translation: str
    matched_terms: List[TermResponse]
    screening: ScreeningResponse
    validation: Dict[str, Any]


class ValidationResponse(BaseModel):
    valid: bool
    missing_terms: List[Dict[str, Any]]
    original_text: str
    translated_text: str    


@app.post(
    "/detect-language",
    response_model=LanguageResponse
)
def detect_language_endpoint(
    request: TextRequest
):
    try:
        language = detect_language(
            request.text
        )

        return LanguageResponse(
            text=request.text,
            detected_language=language
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )    

def get_glossary():
    """
    Load the existing glossary.json file.
    """

    if not GLOSSARY_PATH.exists():
        raise FileNotFoundError(
            f"Glossary file not found: {GLOSSARY_PATH}"
        )

    return load_glossary(
        str(GLOSSARY_PATH)
    )

def extract_terms_from_text(
    text: str
) -> List[Dict[str, Any]]:
    """
    Use the existing Day-3 glossary engine.
    """

    glossary = get_glossary()

    return find_terms(
        text,
        glossary
    )

def format_terms(
    terms: List[Dict[str, Any]]
) -> List[TermResponse]:
    """
    Convert glossary results into API response objects.
    """

    formatted_terms = []

    for term in terms:

        formatted_terms.append(
            TermResponse(
                matched_text=term.get(
                    "matched_text"
                ),

                term_id=term.get(
                    "term_id"
                ),

                category=term.get(
                    "category"
                ),

                preferred_english=(
                    term.get("preferred_english")
                    or term.get("preferred_en")
                    or term.get("english")
                ),

                preferred_hindi=(
                    term.get("preferred_hindi")
                    or term.get("preferred_hi")
                    or term.get("hindi")
                )
            )
        )

    return formatted_terms

@app.post(
    "/extract-terms",
    response_model=ExtractTermsResponse
)
def extract_terms_endpoint(
    request: TextRequest
):

    try:

        language = detect_language(
            request.text
        )

        terms = extract_terms_from_text(
            request.text
        )

        return ExtractTermsResponse(
            text=request.text,
            detected_language=language,
            matched_terms=format_terms(terms)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

@app.post(
    "/validate-translation",
    response_model=ValidationResponse
)
def validate_translation_endpoint(
    request: ValidateTranslationRequest
):

    try:

        target_language = (
            request.target_language.lower()
        )

        terms = extract_terms_from_text(
            request.original_text
        )

        missing_terms = []

        if target_language == "hi":

            for term in terms:

                expected_hi = (
                    term.get("preferred_hindi")
                    or term.get("preferred_hi")
                    or term.get("hindi")
                )

                if (
                    expected_hi
                    and expected_hi
                    not in request.translated_text
                ):

                    missing_terms.append(
                        {
                            "term_id": term.get(
                                "term_id"
                            ),
                            "matched_text": term.get(
                                "matched_text"
                            ),
                            "expected_translation": expected_hi
                        }
                    )

        elif target_language == "en":

            for term in terms:

                expected_en = (
                    term.get("preferred_english")
                    or term.get("preferred_en")
                    or term.get("english")
                )

                if (
                    expected_en
                    and expected_en.lower()
                    not in request.translated_text.lower()
                ):

                    missing_terms.append(
                        {
                            "term_id": term.get(
                                "term_id"
                            ),
                            "matched_text": term.get(
                                "matched_text"
                            ),
                            "expected_translation": expected_en
                        }
                    )

        else:

            raise HTTPException(
                status_code=400,
                detail=(
                    "target_language must be "
                    "'en' or 'hi'."
                )
            )

        return ValidationResponse(
            valid=len(missing_terms) == 0,
            missing_terms=missing_terms,
            original_text=request.original_text,
            translated_text=request.translated_text
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

@app.post(
    "/translate",
    response_model=TranslateResponse
)
def translate_endpoint(
    request: TranslateRequest
):

    try:

        # ----------------------------------------------------
        # STEP 1: Query screening
        # ----------------------------------------------------

        screening = screen_query(
            request.text
        )

        if not screening["valid"]:

            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Query failed screening.",
                    "screening": screening
                }
            )

        # ----------------------------------------------------
        # STEP 2: Detect language
        # ----------------------------------------------------

        detected_language = detect_language(
            request.text
        )

        # ----------------------------------------------------
        # STEP 3: Extract glossary terms
        # ----------------------------------------------------

        terms = extract_terms_from_text(
            request.text
        )

        # ----------------------------------------------------
        # STEP 4: Use existing Day-5 translator
        # ----------------------------------------------------

        final_translation = translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            glossary_path=str(GLOSSARY_PATH)
        )

        # ----------------------------------------------------
        # STEP 5: Validate glossary terminology
        # ----------------------------------------------------

        target_language = (
            request.target_language.lower()
        )

        if target_language not in {"en", "hi"}:

            raise HTTPException(
                status_code=400,
                detail=(
                    "target_language must be "
                    "'en' or 'hi'."
                )
            )

        missing_terms = []

        for term in terms:

            if target_language == "hi":

                expected = (
                    term.get("preferred_hindi")
                    or term.get("preferred_hi")
                    or term.get("hindi")
                )

                found = (
                    expected in final_translation
                    if expected
                    else True
                )

            else:

                expected = (
                    term.get("preferred_english")
                    or term.get("preferred_en")
                    or term.get("english")
                )

                found = (
                    expected.lower()
                    in final_translation.lower()
                    if expected
                    else True
                )

            if not found:

                missing_terms.append(
                    {
                        "term_id": term.get(
                            "term_id"
                        ),
                        "matched_text": term.get(
                            "matched_text"
                        ),
                        "expected_translation": expected
                    }
                )

        validation = {
            "valid": len(missing_terms) == 0,
            "missing_terms": missing_terms
        }

        # ----------------------------------------------------
        # STEP 6: Return complete response
        # ----------------------------------------------------

        return TranslateResponse(
            original_text=request.text,
            detected_language=detected_language,
            source_language=request.source_language,
            target_language=request.target_language,
            translation=final_translation,
            matched_terms=format_terms(terms),
            screening=ScreeningResponse(
                **screening
            ),
            validation=validation
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )