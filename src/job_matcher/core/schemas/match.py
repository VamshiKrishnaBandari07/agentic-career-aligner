from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    openai_configured: bool


class ParseResponse(BaseModel):
    filename: str
    page_count: int
    char_count: int
    text_preview: str = Field(description="First 500 characters of extracted text")


class MatchResponse(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    embedding_similarity: float = Field(ge=0, le=1)
    llm_alignment_score: float = Field(ge=0, le=100)
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    recommendations: list[str]
    summary: str
    metadata: dict
