import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from google import genai

# Multilingual path resolve
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from multilingual.translation.translator import translate

GLOSSARY_FILE = PROJECT_ROOT / "multilingual" / "glossary" / "glossary.json"

from app.schemas.query import QueryRequest, QueryResponse
from app.rag.retrieval import retrieve_documents

load_dotenv()

router = APIRouter(
    prefix="/api/v1",
    tags=["Query"]
)


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in .env"
    )


client = genai.Client(
    api_key=api_key
)

MODEL_NAME = "gemini-3.5-flash"


def calculate_confidence(retrieved_documents):
    """
    Estimate retrieval confidence.

    This represents confidence in the retrieved evidence,
    not legal certainty.

    Lower ranking_score means stronger retrieved evidence.
    """

    if not retrieved_documents:
        return "low"

    best_document = retrieved_documents[0]

    ranking_score = best_document.get(
        "ranking_score"
    )

    if ranking_score is None:
        return "medium"

    # Simple project-level heuristic.
    # These are not scientifically calibrated probabilities.

    if ranking_score <= 0.85:
        return "high"

    if ranking_score <= 1.15:
        return "medium"

    return "low"


def get_translated_query(text: str) -> str:
    if any('\u0900' <= ch <= '\u097F' for ch in text) and GLOSSARY_FILE.exists():
        try:
            return translate(text, glossary_path=str(GLOSSARY_FILE))
        except Exception:
            return text
    return text


@router.post(
    "/query",
    response_model=QueryResponse
)
async def query_assistant(
    request: QueryRequest
):
    try:
        search_query = get_translated_query(request.query)

        retrieved_documents = retrieve_documents(
            search_query,
            request.jurisdiction,
            top_k=5
        )

        if not retrieved_documents:
            return QueryResponse(
                answer=(
                    "I could not find enough relevant "
                    "information in the authoritative "
                    "documents to answer this question."
                ),
                citations=[],
                confidence="low",
                needs_human_review=True
            )

        # -------------------------------------------------------------
        # 2. Calculate retrieval confidence
        # -------------------------------------------------------------

        confidence = calculate_confidence(
            retrieved_documents
        )

        # -------------------------------------------------------------
        # 3. Build evidence for Gemini
        # -------------------------------------------------------------

        evidence_parts = []

        for index, document in enumerate(
            retrieved_documents,
            start=1
        ):
            evidence_parts.append(
                f"""
SOURCE {index}

Source:
{document["source_name"]}

Page:
{document["page_number"]}

Section:
{document.get("section")}

TEXT:
{document["text"]}
"""
            )

        evidence = "\n".join(
            evidence_parts
        )

        # -------------------------------------------------
        # 4. Build grounded Gemini prompt
        # -------------------------------------------------

        prompt = f"""
You are an Indian legal information assistant.

Answer the user's question using ONLY the authoritative
legal excerpts supplied below.

USER QUESTION:
{request.query}

JURISDICTION:
{request.jurisdiction}

RESPONSE LANGUAGE:
{request.language}

AUTHORITATIVE LEGAL EXCERPTS:
{evidence}


RULES:

1. EVIDENCE ONLY

Use only information supported by the supplied excerpts.

2. DO NOT HALLUCINATE

Do not invent:

- sections
- subsections
- Acts
- regulations
- cases
- judgments
- dates
- penalties
- exceptions
- definitions
- legal conclusions

3. INSUFFICIENT INFORMATION

If the supplied excerpts do not contain enough information
to answer the question, clearly say that the available
documents do not provide sufficient information.

Do not use outside knowledge to fill missing information.

4. SECTION NUMBERS

Mention a section number only when it is supported by
the supplied excerpts.

5. SOURCE BOUNDARIES

The supplied excerpts are the only authoritative source
available for this answer.

6. LEGAL ADVICE

Provide general legal information based on the supplied
documents.

Do not present the answer as personalized legal advice.

7. CLARITY

Answer directly and concisely.

Use headings or bullet points when useful.

8. CITATIONS

When explaining a legal rule, identify the relevant
section when that section is present in the evidence.

9. CONFLICTS

If the supplied excerpts appear to conflict, do not
resolve the conflict using outside knowledge.

Clearly identify the conflict.

10. NO OUTSIDE KNOWLEDGE

Do not supplement the answer with your own knowledge.

Before answering, verify that the important claims
are supported by the supplied excerpts.
- If the user's question is in Hindi/Devanagari script, respond completely in Hindi while retaining legal section numbers and statutory acts accurately.
"""


        # -------------------------------------------------
        # 5. Generate grounded answer
        # -------------------------------------------------

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text.strip()


        # -------------------------------------------------
        # 6. Build citations
        # -------------------------------------------------

        citations = []

        for document in retrieved_documents:

            citations.append(
                {
                    "source_name": document[
                        "source_name"
                    ],

                    "page_number": document[
                        "page_number"
                    ],

                    "section": document.get(
                        "section"
                    ),

                    "highlight_text": document[
                        "text"
                    ]
                }
            )


        # -------------------------------------------------
        # 7. Return final response
        # -------------------------------------------------

        return QueryResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            needs_human_review=True
        )


    except Exception as exc:

        print(
            f"Query error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to process the legal query."
        )