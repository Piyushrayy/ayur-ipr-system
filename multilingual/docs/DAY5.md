# DAY 5 — Hindi ↔ English & Bidirectional Flow

## Objective

Day 5 extends the multilingual MVP to support Hindi → English translation,
bidirectional terminology mapping, simple language detection, and
English-centric RAG preparation.

## What Was Implemented

### 1. Hindi → English Glossary Mapping

The glossary engine was extended to recognize:

- Preferred English terms
- English aliases
- Preferred Hindi terms
- Hindi aliases

Examples:

| Hindi Term | Canonical English |
|---|---|
| पेटेंट | Patent |
| पूर्व कला | Prior Art |
| पारंपरिक ज्ञान | Traditional Knowledge |
| आयुर्वेद | Ayurveda |

This allows the same glossary engine to detect technical terminology
regardless of whether the user writes the query in Hindi or English.

### 2. Hindi Unicode Normalization

The `normalize_term()` function was updated to preserve Hindi/Devanagari
characters and combining marks during normalization.

It supports:

- Unicode normalization
- Case-insensitive normalization
- Hyphen/underscore normalization
- Punctuation cleanup
- Whitespace normalization

This prevents Hindi terms from being broken into incorrect characters.

### 3. Bidirectional Translation

The translation layer now supports:

```text
English → Hindi
Hindi → English