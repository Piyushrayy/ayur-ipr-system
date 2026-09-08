import json
import os
import chromadb
from chromadb.utils import embedding_functions

# 1. Load the Day 1 extracted JSON file
def load_extracted_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 2. Stage 2: Create Section-Aware Chunks
def create_section_chunks(data):
    chunks = []
    
    for item in data:
        text = item["text"]
        page_num = item["page_number"]
        bbox = item["bbox"]
        
        # Simple section awareness: look for key legal terms in text
        section_name = "General Provision"
        if "Section" in text or "SECTION" in text:
            # Extract section title line if present
            first_line = text.split("\n")[0]
            section_name = first_line[:50]  # Grab first 50 chars as section header

        chunks.append({
            "text": text,
            "metadata": {
                "document_id": "patents_act_1970",
                "source_name": "Patents Act 1970",
                "page_number": page_num,
                "section": section_name,
                "bbox": str(bbox)  # ChromaDB metadata must be strings, ints, or floats
            }
        })
        
    return chunks

# 3. Stage 3: Store Chunks into ChromaDB
def store_in_chromadb(chunks, db_path="./chroma_db"):
    # Initialize ChromaDB local client
    client = chromadb.PersistentClient(path=db_path)
    
    # Use a standard, lightweight embedding model
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="legal_documents",
        embedding_function=emb_fn
    )
    
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [f"doc_chunk_{i}" for i in range(len(chunks))]
    
    # Add to database
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Successfully stored {len(chunks)} chunks in ChromaDB at '{db_path}'!")
    return collection

# 4. Stage 4: Test Retrieval
def test_retrieval(collection, query_text):
    print(f"\n--- Testing Search Query: '{query_text}' ---")
    results = collection.query(
        query_texts=[query_text],
        n_results=2  # Get top 2 matching chunks
    )
    
    for i in range(len(results["documents"][0])):
        print(f"\n[Match {i+1}]")
        print(f"Text: {results['documents'][0][i][:150]}...")
        print(f"Page Number: {results['metadatas'][0][i]['page_number']}")
        print(f"Section: {results['metadatas'][0][i]['section']}")
        print(f"BBox Coordinates: {results['metadatas'][0][i]['bbox']}")

if __name__ == "__main__":
    json_file = "ingestion/extracted_output.json"
    
    if os.path.exists(json_file):
        print("1. Loading Day 1 JSON...")
        data = load_extracted_json(json_file)
        
        print("2. Stage 2: Building section-aware chunks...")
        chunks = create_section_chunks(data)
        
        print("3. Stage 3: Ingesting into ChromaDB...")
        collection = store_in_chromadb(chunks)
        
        print("4. Stage 4: Verifying vector retrieval...")
        test_retrieval(collection, "patent traditional knowledge ayurveda")
    else:
        print(f"Error: {json_file} not found. Run Day 1 script first!")