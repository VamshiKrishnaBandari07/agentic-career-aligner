from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    openai_configured: bool
    match_provider: str
    free_mode: bool
    serve_ui: bool = False
    ready: bool = True


class ParseResponse(BaseModel):
    filename: str
    page_count: int
    char_count: int
    text_preview: str = Field(description="First 500 characters of extracted text")


class MatchResponse(BaseModel):
    overall_score: float = Field(ge=0, le=100, description="Weighted match score 0-100")
    embedding_similarity: float = Field(ge=0, le=1)
    llm_alignment_score: float = Field(ge=0, le=100)
    matched_skills: list[str] = Field(description="Skills from the job that your resume demonstrates")
    missing_skills: list[str] = Field(description="Technical skills required by the job but not found on resume")
    missing_requirements: list[str] = Field(
        description="Other job requirements missing from resume (tools, domains, responsibilities)"
    )
    missing_qualifications: list[str] = Field(
        description="Education, certifications, or years of experience gaps"
    )
    missing_experience: list[str] = Field(
        description="Specific experience areas the job asks for that resume lacks"
    )
    strengths: list[str] = Field(description="What you already do well for this role")
    recommendations: list[str] = Field(description="How to improve your resume for this job")
    action_items: list[str] = Field(description="Concrete next steps to close the gap")
    resume_suggestions: list[str] = Field(
        description="Specific edits to make on your resume for this job"
    )
    summary: str = Field(description="Overall fit summary in plain language")
    metadata: dict
