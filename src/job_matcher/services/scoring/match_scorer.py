from dataclasses import dataclass

from job_matcher.core.config import Settings
from job_matcher.core.models.match_result import ComparisonResult


@dataclass
class ScoreBreakdown:
    overall_score: float
    embedding_similarity: float
    llm_alignment_score: float


class MatchScorer:
    def __init__(self, settings: Settings) -> None:
        self._embedding_weight = settings.embedding_weight
        self._llm_weight = settings.llm_weight

    def score(
        self, embedding_similarity: float, comparison: ComparisonResult
    ) -> ScoreBreakdown:
        llm_score = max(0.0, min(100.0, comparison.llm_score))
        sim = max(0.0, min(1.0, embedding_similarity))
        overall = (
            self._embedding_weight * (sim * 100) + self._llm_weight * llm_score
        )
        return ScoreBreakdown(
            overall_score=round(overall, 2),
            embedding_similarity=round(sim, 4),
            llm_alignment_score=round(llm_score, 2),
        )
