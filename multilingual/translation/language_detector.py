import re


DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")
ENGLISH_PATTERN = re.compile(r"[A-Za-z]")


def detect_language(text: str) -> str:
    """
    Detect whether text is primarily Hindi, English, or mixed.

    Returns:
        "hi"     -> Hindi
        "en"     -> English
        "mixed"  -> Hindi + English
        "unknown"-> No meaningful language characters
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip()

    if not text:
        return "unknown"

    hindi_chars = len(DEVANAGARI_PATTERN.findall(text))
    english_chars = len(ENGLISH_PATTERN.findall(text))

    if hindi_chars == 0 and english_chars == 0:
        return "unknown"

    # Both languages are present.
    if hindi_chars > 0 and english_chars > 0:
        return "mixed"

    if hindi_chars > 0:
        return "hi"

    return "en"