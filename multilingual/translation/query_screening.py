import re
from typing import Any, Dict


def screen_query(text: str) -> Dict[str, Any]:
    """
    Perform lightweight query screening before translation.

    This is an MVP grammatical/query-quality screening layer.
    It does not replace a full grammar model.

    Checks:
    - empty input
    - excessive whitespace
    - repeated words
    - obvious punctuation problems
    - very short/incomplete queries
    - unmatched brackets
    """

    issues = []
    warnings = []

    # ---------------------------------------------------------
    # 1. Input type check
    # ---------------------------------------------------------

    if not isinstance(text, str):
        return {
            "valid": False,
            "grammar_ok": False,
            "issues": ["Query must be a string."],
            "warnings": []
        }

    text = text.strip()

    # ---------------------------------------------------------
    # 2. Empty query
    # ---------------------------------------------------------

    if not text:
        return {
            "valid": False,
            "grammar_ok": False,
            "issues": ["Query cannot be empty."],
            "warnings": []
        }

    # ---------------------------------------------------------
    # 3. Excessive whitespace
    # ---------------------------------------------------------

    if re.search(r"\s{3,}", text):
        warnings.append(
            "Query contains excessive whitespace."
        )

    # ---------------------------------------------------------
    # 4. Repeated words
    # ---------------------------------------------------------

    repeated_words = re.findall(
        r"\b(\w+)\s+\1\b",
        text,
        flags=re.IGNORECASE
    )

    if repeated_words:
        issues.append(
            "Repeated words detected: "
            + ", ".join(repeated_words)
        )

    # ---------------------------------------------------------
    # 5. Repeated punctuation
    # ---------------------------------------------------------

    if re.search(r"[!?.,]{3,}", text):
        warnings.append(
            "Query contains excessive punctuation."
        )

    # ---------------------------------------------------------
    # 6. Unmatched brackets
    # ---------------------------------------------------------

    bracket_pairs = {
        "(": ")",
        "[": "]",
        "{": "}"
    }

    for opening, closing in bracket_pairs.items():

        if text.count(opening) != text.count(closing):
            issues.append(
                f"Unmatched bracket: {opening} or {closing}"
            )

    # ---------------------------------------------------------
    # 7. Very short query
    # ---------------------------------------------------------

    words = text.split()

    if len(words) == 1:
        warnings.append(
            "Query contains only one word."
        )

    # ---------------------------------------------------------
    # 8. Basic sentence structure check
    # ---------------------------------------------------------

    if len(words) >= 3:

        first_word = words[0]

        if first_word.islower():
            warnings.append(
                "Sentence does not begin with a capital letter."
            )

    # ---------------------------------------------------------
    # 9. Detect obvious incomplete English questions
    # ---------------------------------------------------------

    lowered = text.lower()

    incomplete_patterns = [
        r"^how$",
        r"^what$",
        r"^why$",
        r"^where$",
        r"^when$",
        r"^which$"
    ]

    for pattern in incomplete_patterns:

        if re.fullmatch(pattern, lowered):
            issues.append(
                "The query appears incomplete."
            )

    # ---------------------------------------------------------
    # 10. Final result
    # ---------------------------------------------------------

    grammar_ok = len(issues) == 0

    return {
        "valid": grammar_ok,
        "grammar_ok": grammar_ok,
        "issues": issues,
        "warnings": warnings
    }