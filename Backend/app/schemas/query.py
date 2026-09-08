from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's legal or IPR question")
    language: str = Field(default="en", description="Response language")
    jurisdiction: str = Field(
        default="india",
        description="Legal jurisdiction: india or international"
    )


class Citation(BaseModel):
    source_name: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    highlight_text: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: str
    needs_human_review: bool