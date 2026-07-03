from dataclasses import dataclass, field


@dataclass
class ComparisonResult:
    llm_score: float
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)
    missing_qualifications: list[str] = field(default_factory=list)
    missing_experience: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    resume_suggestions: list[str] = field(default_factory=list)
    summary: str = ""
