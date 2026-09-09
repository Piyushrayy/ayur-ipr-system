# HERBAL_ROOTS Multilingual API

## Overview

The HERBAL_ROOTS Multilingual API provides a FastAPI interface
for the English-Hindi glossary-anchored translation pipeline.

The API supports:

- Language detection
- Glossary term extraction
- Bidirectional translation
- Translation validation
- Query screening


## Start the API

From the `HERBAL_ROOTS` project root:

```powershell
python -m uvicorn multilingual.api.multilingual_api:app --reload