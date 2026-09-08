import hashlib
import json
import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from app.ingestion.parse_pdf import extract_pdf_blocks


# -------------------------------------------------
# Configuration
# -------------------------------------------------

DOCUMENTS_DIR = "app/data/documents"
CHROMA_DIR = "app/data/vector_db"
COLLECTION_NAME = "legal_documents"

MODEL_NAME = "all-MiniLM-L6-v2"


# -------------------------------------------------
# File utilities
# -------------------------------------------------

def calculate_file_hash(file_path):
    """
    Calculate SHA-256 hash of the PDF.

    This uniquely identifies the exact file/version.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def create_document_id(file_path):
    """
    Create a stable document ID from the filename.
    """

    return (
        Path(file_path)
        .stem
        .lower()
        .replace(" ", "_")
    )


def create_source_name(file_path):
    """
    Convert filename into a readable source name.

    Example:
        patentact_1970_india.pdf
        -> Patentact 1970 India
    """

    return (
        Path(file_path)
        .stem
        .replace("_", " ")
        .title()
    )


def get_jurisdiction(file_path):
    """
    Determine jurisdiction from the parent folder.

    Expected structure:

        documents/
            indian/
            international/
    """

    parent_folder = (
        Path(file_path)
        .parent
        .name
        .lower()
    )

    if parent_folder == "indian":
        return "india"

    if parent_folder == "international":
        return "international"

    raise ValueError(
        f"Unknown jurisdiction folder for: {file_path}\n"
        f"Expected 'indian' or 'international'."
    )


def find_pdf_documents():
    """
    Find PDFs inside both jurisdiction folders.
    """

    documents_path = Path(DOCUMENTS_DIR)

    if not documents_path.exists():
        print(
            f"Documents directory not found: "
            f"{DOCUMENTS_DIR}"
        )
        return []

    pdf_files = []

    for jurisdiction_folder in [
        "indian",
        "international"
    ]:

        folder = (
            documents_path
            / jurisdiction_folder
        )

        if not folder.exists():
            print(
                f"Warning: folder not found: {folder}"
            )
            continue

        pdf_files.extend(
            folder.glob("*.pdf")
        )

    return sorted(pdf_files)


# -------------------------------------------------
# Text processing
# -------------------------------------------------

def clean_blocks(blocks):
    """
    Remove very small junk blocks.
    """

    cleaned = []

    for block in blocks:

        text = block["text"].strip()

        if len(text) < 20:
            continue

        cleaned.append(block)

    return cleaned


def create_chunks(blocks, max_chars=1200):
    """
    Convert extracted PDF blocks into chunks.
    """

    chunks = []

    current_text = ""
    current_page = None
    current_bboxes = []

    for block in blocks:

        text = block["text"]
        page = block["page_number"]
        bbox = block["bbox"]

        # Start a new chunk when:
        # 1. Page changes
        # 2. Maximum chunk size is reached
        if (
            current_text
            and (
                page != current_page
                or len(current_text) + len(text)
                > max_chars
            )
        ):

            chunks.append(
                {
                    "text": current_text.strip(),
                    "page_number": current_page,
                    "bboxes": current_bboxes,
                }
            )

            current_text = ""
            current_bboxes = []

        if not current_text:
            current_page = page

        current_text += text + "\n"
        current_bboxes.append(bbox)

    # Store final chunk.
    if current_text.strip():

        chunks.append(
            {
                "text": current_text.strip(),
                "page_number": current_page,
                "bboxes": current_bboxes,
            }
        )

    return chunks


# -------------------------------------------------
# Main ingestion pipeline
# -------------------------------------------------

def build_vector_database():

    print("=" * 60)
    print("LEGAL DOCUMENT INGESTION")
    print("=" * 60)

    # -------------------------------------------------
    # 1. Discover PDFs
    # -------------------------------------------------

    pdf_files = find_pdf_documents()

    if not pdf_files:

        print("No PDF documents found.")

        return

    print()
    print(
        f"Found {len(pdf_files)} PDF document(s):"
    )

    for pdf_file in pdf_files:

        jurisdiction = get_jurisdiction(
            pdf_file
        )

        print(
            f"  [{jurisdiction}] "
            f"{pdf_file.name}"
        )

    # -------------------------------------------------
    # 2. Process documents
    # -------------------------------------------------

    all_chunks = []

    for pdf_file in pdf_files:

        print()
        print("-" * 60)
        print(
            f"Processing: {pdf_file.name}"
        )

        jurisdiction = get_jurisdiction(
            pdf_file
        )

        document_id = create_document_id(
            pdf_file
        )

        source_name = create_source_name(
            pdf_file
        )

        file_hash = calculate_file_hash(
            pdf_file
        )

        print(
            f"Jurisdiction: {jurisdiction}"
        )

        print(
            f"Document ID: {document_id}"
        )

        print(
            f"Source: {source_name}"
        )

        print(
            f"SHA-256: {file_hash[:16]}..."
        )

        # Extract PDF blocks.
        blocks = extract_pdf_blocks(
            str(pdf_file)
        )

        print(
            f"Extracted blocks: {len(blocks)}"
        )

        # Clean extracted blocks.
        blocks = clean_blocks(
            blocks
        )

        print(
            f"Clean blocks: {len(blocks)}"
        )

        # Create chunks.
        chunks = create_chunks(
            blocks
        )

        print(
            f"Created chunks: {len(chunks)}"
        )

        # Attach metadata to every chunk.
        for chunk_index, chunk in enumerate(
            chunks
        ):

            all_chunks.append(
                {
                    "text": chunk["text"],
                    "page_number": chunk[
                        "page_number"
                    ],
                    "bboxes": chunk[
                        "bboxes"
                    ],
                    "document_id": document_id,
                    "source_name": source_name,
                    "source_file": pdf_file.name,
                    "jurisdiction": jurisdiction,
                    "file_hash": file_hash,
                    "chunk_index": chunk_index,
                }
            )

    # -------------------------------------------------
    # 3. Summary
    # -------------------------------------------------

    print()
    print("=" * 60)
    print(
        f"Documents processed: {len(pdf_files)}"
    )
    print(
        f"Total chunks: {len(all_chunks)}"
    )
    print("=" * 60)

    # -------------------------------------------------
    # 4. Load embedding model
    # -------------------------------------------------

    print()
    print("Loading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    # -------------------------------------------------
    # 5. Connect to ChromaDB
    # -------------------------------------------------

    os.makedirs(
        CHROMA_DIR,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=CHROMA_DIR
    )

    # Rebuild the complete collection.
    try:

        client.delete_collection(
            COLLECTION_NAME
        )

        print(
            f"Deleted existing collection: "
            f"{COLLECTION_NAME}"
        )

    except Exception:

        pass

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    # -------------------------------------------------
    # 6. Generate embeddings
    # -------------------------------------------------

    print()
    print("Generating embeddings...")

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    ).tolist()

    # -------------------------------------------------
    # 7. Create Chroma records
    # -------------------------------------------------

    ids = []
    metadatas = []

    for index, chunk in enumerate(
        all_chunks
    ):

        chunk_id = (
            f"{chunk['document_id']}_"
            f"{chunk['chunk_index']}_"
            f"{index}"
        )

        ids.append(
            chunk_id
        )

        metadatas.append(
            {
                "document_id": chunk[
                    "document_id"
                ],

                "source_name": chunk[
                    "source_name"
                ],

                "source_file": chunk[
                    "source_file"
                ],

                "jurisdiction": chunk[
                    "jurisdiction"
                ],

                "file_hash": chunk[
                    "file_hash"
                ],

                "page_number": chunk[
                    "page_number"
                ],

                "bbox_json": json.dumps(
                    chunk["bboxes"]
                ),
            }
        )

    # -------------------------------------------------
    # 8. Store vectors
    # -------------------------------------------------

    print()
    print(
        "Storing vectors in ChromaDB..."
    )

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    # -------------------------------------------------
    # 9. Final result
    # -------------------------------------------------

    print()
    print("=" * 60)
    print(
        "VECTOR DATABASE CREATED SUCCESSFULLY"
    )
    print("=" * 60)

    print(
        f"Documents processed: "
        f"{len(pdf_files)}"
    )

    print(
        f"Chunks stored: "
        f"{len(all_chunks)}"
    )

    print(
        f"Collection: "
        f"{COLLECTION_NAME}"
    )

    print(
        f"Database location: "
        f"{CHROMA_DIR}"
    )

    print("=" * 60)


if __name__ == "__main__":
    build_vector_database()