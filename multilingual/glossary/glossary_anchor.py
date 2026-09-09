import json
import re
import unicodedata
from pathlib import Path
from typing import Any


def load_glossary(glossary_path: str | Path) -> list[dict[str, Any]]:
    """
    Load glossary terms from a JSON file.

    Supports both glossary formats:

    Format 1:
    {
        "terms": [
            {
                "term_id": "...",
                "english": "...",
                "hindi": "...",
                ...
            }
        ]
    }

    Format 2:
    [
        {
            "term_id": "...",
            "english": "...",
            "hindi": "...",
            ...
        }
    ]

    Both formats are converted into the internal structure
    expected by the glossary anchor engine.
    """

    path = Path(glossary_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Glossary file not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    # --------------------------------------------------------
    # Support both glossary formats
    # --------------------------------------------------------

    if isinstance(data, dict):
        terms = data.get("terms")

        if not isinstance(terms, list):
            raise ValueError(
                "Glossary object must contain a 'terms' list."
            )

    elif isinstance(data, list):
        terms = data

    else:
        raise ValueError(
            "Glossary root must be either a JSON object "
            "or a JSON list."
        )

    # --------------------------------------------------------
    # Convert entries to the standard internal structure
    # --------------------------------------------------------

    normalized_terms = []

    for entry in terms:

        if not isinstance(entry, dict):
            continue

        normalized_entry = {
            "term_id": entry.get("term_id", ""),
            "category": entry.get("category", ""),

            # Support your actual glossary field names
            "preferred_english": entry.get(
                "preferred_english",
                entry.get("english", "")
            ),

            "preferred_hindi": entry.get(
                "preferred_hindi",
                entry.get("hindi", "")
            ),

            # Support both alias formats
            "aliases": entry.get(
                "aliases",
                entry.get("aliases_en", [])
            ),

            # Preserve additional information
            "aliases_hi": entry.get(
                "aliases_hi",
                []
            ),

            "do_not_translate": entry.get(
                "do_not_translate",
                False
            ),

            "context": entry.get(
                "context",
                ""
            ),

            "explanation_en": entry.get(
                "explanation_en",
                ""
            ),

            "explanation_hi": entry.get(
                "explanation_hi",
                ""
            )
        }

        # Skip invalid entries without a term ID
        if not normalized_entry["term_id"]:
            continue

        normalized_terms.append(normalized_entry)

    return normalized_terms


def normalize_term(term: str) -> str:
    """
    Normalize text for glossary matching.

    Supports:
    - English
    - Hindi / Devanagari
    - case-insensitive matching
    - hyphen/underscore normalization
    - punctuation cleanup
    - whitespace normalization
    """

    if not isinstance(term, str):
        raise TypeError("term must be a string")

    # --------------------------------------------------------
    # Unicode normalization
    # --------------------------------------------------------

    term = unicodedata.normalize(
        "NFKC",
        term
    )

    # --------------------------------------------------------
    # Case-insensitive normalization
    #
    # Works for English and does not damage Hindi.
    # --------------------------------------------------------

    term = term.casefold()

    # --------------------------------------------------------
    # Convert hyphens and underscores to spaces
    # --------------------------------------------------------

    term = re.sub(
        r"[-_]+",
        " ",
        term
    )

    # --------------------------------------------------------
    # Remove punctuation, but KEEP Unicode letters,
    # numbers, combining marks and whitespace.
    #
    # We intentionally do NOT use [^\w\s] here because
    # that can damage Devanagari combining characters.
    # --------------------------------------------------------

    cleaned_chars = []

    for char in term:

        category = unicodedata.category(char)

        if (
            char.isspace()
            or category[0] in {"L", "N", "M"}
        ):
            cleaned_chars.append(char)
        else:
            cleaned_chars.append(" ")

    term = "".join(cleaned_chars)

    # --------------------------------------------------------
    # Collapse multiple spaces
    # --------------------------------------------------------

    term = re.sub(
        r"\s+",
        " ",
        term
    )

    return term.strip()


def _build_alias_map(
    glossary: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """
    Build:

        normalized alias -> glossary entry

    Supports both English and Hindi terminology.

    Searchable forms include:
    - preferred English
    - English aliases
    - preferred Hindi
    - Hindi aliases
    """

    alias_map: dict[str, dict[str, Any]] = {}

    for entry in glossary:

        term_id = entry.get("term_id")

        if not term_id:
            continue

        # ----------------------------------------------------
        # English forms
        # ----------------------------------------------------

        preferred_english = (
            entry.get("preferred_english")
            or entry.get("preferred_en")
            or entry.get("english")
            or ""
            
        )

        english_aliases = (
            entry.get("aliases")
            or entry.get("aliases_en")
            or []
            
        )

        # Support aliases_en explicitly as well.
        aliases_en = (
            entry.get("aliases_en")
            or []
        )

        # ----------------------------------------------------
        # Hindi forms
        # ----------------------------------------------------

        preferred_hindi = (
            entry.get("preferred_hindi")
            or entry.get("preferred_hi")
            or entry.get("hindi")
            or ""
            
        )

        hindi_aliases = (
            entry.get("aliases_hi")
            or []
            
        )

        # ----------------------------------------------------
        # Combine every searchable form
        # ----------------------------------------------------

        all_aliases = []

        if preferred_english:
            all_aliases.append(
                preferred_english
            )

        if isinstance(english_aliases, list):
            all_aliases.extend(
                english_aliases
            )
        elif isinstance(english_aliases, str):
            all_aliases.append(
                english_aliases
            )

        if isinstance(aliases_en, list):
            all_aliases.extend(
                aliases_en
            )
        elif isinstance(aliases_en, str):
            all_aliases.append(
                aliases_en
            )

        if preferred_hindi:
            all_aliases.append(
                preferred_hindi
            )

        if isinstance(hindi_aliases, list):
            all_aliases.extend(
                hindi_aliases
            )
        elif isinstance(hindi_aliases, str):
            all_aliases.append(
                hindi_aliases
            )

        # ----------------------------------------------------
        # Add normalized aliases to map
        # ----------------------------------------------------

        for alias in all_aliases:

            if not isinstance(alias, str):
                continue

            normalized_alias = normalize_term(
                alias
            )

            if normalized_alias:
                alias_map[
                    normalized_alias
                ] = entry

    return alias_map


def find_terms(
    text: str,
    glossary: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Find glossary terms inside text.

    Matching is:
    - case-insensitive
    - alias-aware
    - tolerant of hyphen/space variations
    - boundary-aware

    Returns matched text, location, term ID,
    category and preferred forms.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    alias_map = _build_alias_map(glossary)

    if not alias_map:
        return []

    matches: list[dict[str, Any]] = []

    # Longer aliases first to avoid partial matches.
    aliases = sorted(
        alias_map.keys(),
        key=len,
        reverse=True
    )

    for alias in aliases:

        entry = alias_map[alias]

        # Convert normalized alias to a regex pattern.
        # Spaces are allowed to match one or more spaces/hyphens.
        words = alias.split()

        pattern_parts = []

        for word in words:
            pattern_parts.append(re.escape(word))

        pattern = r"[\s\-_]+".join(pattern_parts)

        regex = re.compile(
            rf"(?<!\w){pattern}(?!\w)",
            flags=re.IGNORECASE | re.UNICODE
        )

        for match in regex.finditer(text):

            matches.append(
                {
                    "matched_text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "term_id": entry["term_id"],
                    "category": entry.get("category", ""),
                    "preferred_english": (
                        entry.get("preferred_english")
                        or entry.get("preferred_en")
                        or entry.get("english")
                        or ""
                    ),
                    "preferred_hindi": (
                        entry.get("preferred_hindi")
                        or entry.get("preferred_hi")
                        or entry.get("hindi")
                        or ""
                    )
                }
            )

    # Sort by position first.
    matches.sort(
        key=lambda item: (
            item["start"],
            -(item["end"] - item["start"])
        )
    )

    # Remove overlapping matches.
    non_overlapping: list[dict[str, Any]] = []

    current_end = -1

    for match in matches:

        if match["start"] >= current_end:
            non_overlapping.append(match)
            current_end = match["end"]

    return non_overlapping


def get_translation(
    term_id: str,
    glossary: list[dict[str, Any]],
    language: str = "hindi"
) -> str | None:
    """
    Get the preferred translation/form for a term ID.

    language:
        hindi
        english
    """

    if not isinstance(term_id, str):
        raise TypeError("term_id must be a string")

    language = language.casefold()

    for entry in glossary:

        if entry.get("term_id") != term_id:
            continue

        if language == "hindi":
            return entry.get("preferred_hindi")

        if language == "english":
            return entry.get("preferred_english")

        raise ValueError(
            "language must be 'hindi' or 'english'"
        )

    return None


def create_anchors(
    text: str,
    glossary: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Create structured glossary anchors from input text.
    """

    matches = find_terms(text, glossary)

    anchors = []

    for match in matches:

        anchors.append(
            {
                "matched_text": match["matched_text"],
                "term_id": match["term_id"],
                "category": match["category"],
                "preferred_english": match[
                    "preferred_english"
                ],
                "preferred_hindi": match[
                    "preferred_hindi"
                ],
                "start": match["start"],
                "end": match["end"]
            }
        )

    return anchors