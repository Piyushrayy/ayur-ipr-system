# HERBAL_ROOTS — Multilingual Ingestion 🌿

This module prepares patent and Ayurvedic-related knowledge for multilingual RAG.

## Workflow

```text
Raw Documents
     ↓
Data Collection
     ↓
Text Extraction
     ↓
Cleaning & Chunking
     ↓
Glossary / Terminology Mapping
     ↓
Multilingual Translation
     ↓
Validation & Testing
     ↓
Processed Data
     ↓
RAG / Vector Database

multilingual/
│
├── data/          # Raw and processed documents/data
│
├── glossary/      # Patent & Ayurvedic terminology
│
├── translation/   # Multilingual translation pipeline
│
├── api/           # APIs for multilingual processing
│
├── tests/         # Testing and validation
│
└── docs/          # Documentation