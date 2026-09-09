# English → Hindi Translation Layer

## Purpose

The translation layer converts English text into Hindi while preserving important terminology defined by the multilingual glossary.

## Workflow

```text
English Input
      ↓
Glossary Term Detection
      ↓
Terminology Protection
      ↓
English → Hindi Translation
      ↓
Preferred Terminology Restoration
      ↓
Validation
      ↓
Hindi Output
```

## Terminology Anchoring vs Ordinary Translation

Ordinary English → Hindi translation allows the translation model to decide how terms should be translated.

Terminology anchoring adds a controlled glossary layer.

For example:

```text
Patent
   ↓
पेटेंट
```

The translation provider is prevented from freely changing the protected term.

The system temporarily replaces important terms with placeholders:

```text
Patent protection is important.
```

becomes:

```text
__TERM_0__ protection is important.
```

The translation provider translates the remaining sentence.

After translation, the placeholder is restored using the preferred Hindi terminology from the glossary.

```text
__TERM_0__ संरक्षण महत्वपूर्ण है।
```

becomes:

```text
पेटेंट संरक्षण महत्वपूर्ण है।
```

## Why Anchoring Is Important

Terminology anchoring provides:

* Consistent technical terminology
* Consistent patent terminology
* Better handling of Ayurveda-related terminology
* Better preservation of Traditional Knowledge terminology
* Controlled Hindi terminology
* Easier validation
* Independence from a particular translation provider

## Replaceable Translation Provider

The system uses a `TranslationProvider` interface.

This means the translation layer does not depend on one specific translation service.

A future implementation can connect:

* A cloud translation API
* A large language model
* A dedicated machine translation model
* A locally hosted translation model

without changing the main glossary-protection pipeline.

## Validation

After translation, the system checks whether all preferred Hindi terminology detected by the glossary appears in the final output.

Example:

```text
Expected:
पेटेंट

Found:
पेटेंट

Result:
VALID
```

If an expected term is missing, the validation result becomes invalid and identifies the missing terminology.

## Day 4 Goal

The goal is not to build a complete production translation service.

The goal is to establish a reliable architecture in which:

```text
Glossary
   +
Translation Provider
   +
Terminology Anchoring
   +
Validation
```

work together as a reusable English → Hindi translation layer.
