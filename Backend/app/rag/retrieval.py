import re

import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = "app/data/vector_db"

COLLECTION_NAME = "legal_documents"

MODEL_NAME = "all-MiniLM-L6-v2"

# Maximum semantic distance allowed.
# Lower distance = more semantically relevant.
MAX_DISTANCE = 1.35

# Retrieve more candidates first, then rank and return the best ones.
CANDIDATE_COUNT = 20


# Load the embedding model once when the application starts.
model = SentenceTransformer(MODEL_NAME)


# Connect to the existing ChromaDB database.
client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_collection(
    name=COLLECTION_NAME
)


def extract_requested_section(query: str):
    """
    Detect whether the user explicitly asked for a section number.

    Examples:
        "What does Section 4 say?"
        -> "4"

        "Explain section 48"
        -> "48"

        "What are not patentable inventions?"
        -> None
    """

    match = re.search(
        r"\bsection\s+(\d+[A-Za-z]?)\b",
        query,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return None


def extract_section(text: str):
    """
    Try to extract the main section number from a legal text chunk.

    Handles normal legal formatting as well as common OCR artifacts.
    """

    patterns = [

        # Normal format:
        # 4. Inventions relating to atomic energy...
        r"(?m)^\s*(?:\d+\[)?(\d+[A-Za-z]?)\.\s+[A-Z]",

        # OCR format where a footnote marker appears:
        # 1[65. Revocation...
        r"(?m)^\s*\d+\[(\d+[A-Za-z]?)\.\s+[A-Z]",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return f"Section {match.group(1)}"

    return None


def section_matches(
    query_section,
    document_section
):
    """
    Check whether the section requested by the user
    matches the section identified in the retrieved document.
    """

    if not query_section or not document_section:
        return False

    document_number = re.search(
        r"Section\s+(\d+[A-Za-z]?)",
        document_section,
        re.IGNORECASE
    )

    if not document_number:
        return False

    return (
        query_section.lower()
        == document_number.group(1).lower()
    )


def retrieve_documents(
    query: str,
    jurisdiction: str,
    top_k: int = 5
):
    """
    Retrieve relevant chunks from the legal document database.

    Process:
        1. Filter documents by jurisdiction.
        2. Retrieve a larger candidate pool.
        3. Remove weak semantic matches.
        4. Detect section numbers.
        5. Boost an explicitly requested section.
        6. Sort by ranking score.
        7. Return the best top_k documents.
    """

    # -------------------------------------------------
    # Validate jurisdiction
    # -------------------------------------------------

    jurisdiction = jurisdiction.lower().strip()

    if jurisdiction not in {
        "india",
        "international"
    }:
        raise ValueError(
            "Jurisdiction must be 'india' "
            "or 'international'."
        )

    # -------------------------------------------------
    # Create query embedding
    # -------------------------------------------------

    query_embedding = model.encode(
        query
    ).tolist()

    # Retrieve more candidates than we ultimately return.
    candidate_count = max(
        top_k,
        CANDIDATE_COUNT
    )

    # -------------------------------------------------
    # Jurisdiction-filtered vector search
    # -------------------------------------------------

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],

        n_results=candidate_count,

        where={
            "jurisdiction": jurisdiction
        }
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    requested_section = (
        extract_requested_section(query)
    )

    retrieved_documents = []

    # -------------------------------------------------
    # Rank retrieved documents
    # -------------------------------------------------

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # Ignore weak semantic matches.
        if distance > MAX_DISTANCE:
            continue

        detected_section = extract_section(
            document
        )

        # Give an explicitly requested section
        # a ranking advantage.
        section_match = section_matches(
            requested_section,
            detected_section
        )

        # Lower score = better.
        ranking_score = distance

        if section_match:
            ranking_score -= 0.50

        retrieved_documents.append(
            {
                "text": document,

                "source_name": metadata.get(
                    "source_name",
                    "Unknown legal document"
                ),

                "source_file": metadata.get(
                    "source_file"
                ),

                "document_id": metadata.get(
                    "document_id"
                ),

                "jurisdiction": metadata.get(
                    "jurisdiction"
                ),

                "page_number": metadata.get(
                    "page_number"
                ),

                "section": detected_section,

                "distance": distance,

                "ranking_score": ranking_score,

                "section_match": section_match
            }
        )

    # -------------------------------------------------
    # Best results first
    # -------------------------------------------------

    retrieved_documents.sort(
        key=lambda x: x["ranking_score"]
    )

    # Return only requested number of results.
    return retrieved_documents[:top_k]