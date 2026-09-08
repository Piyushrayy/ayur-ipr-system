from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    jurisdiction: str
    language: str

@app.post("/api/v1/query")
def mock_query(req: QueryRequest):
    # If out of scope, simulate safe abstention
    if "tax" in req.query.lower() or "crude oil" in req.query.lower():
        return {
            "answer": "Out of scope legal query.",
            "abstain": True,
            "citations": []
        }

    # Return mock citation matching your dataset schema
    return {
        "answer": "Traditional knowledge cannot be patented under Section 3(p).",
        "abstain": False,
        "citations": [
            {
                "document_id": "patents_act",
                "source_name": "The Patents Act, 1970",
                "section": "Section 3(p)",
                "text": "Inventions relating to traditional knowledge are not patentable under Section 3(p)."
            }
        ]
    }