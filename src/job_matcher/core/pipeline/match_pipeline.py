import time
from dataclasses import dataclass

from job_matcher.core.config import Settings
from job_matcher.core.models.document import ParsedDocument
from job_matcher.core.schemas.match import MatchResponse
from job_matcher.services.comparison.cosine_similarity import cosine_similarity
from job_matcher.services.comparison.llm_comparator import LLMComparator
from job_matcher.services.comparison.local_comparator import LocalComparator
from job_matcher.services.embedding.local_embedder import LocalEmbedder
from job_matcher.services.embedding.openai_embedder import OpenAIEmbedder
from job_matcher.services.pdf.pymupdf_parser import PyMuPDFParser
from job_matcher.services.scoring.match_scorer import MatchScorer
from job_matcher.utils.text_document import build_job_document


@dataclass
class MatchPipeline:
    settings: Settings
    pdf_parser: PyMuPDFParser
    embedder: LocalEmbedder | OpenAIEmbedder
    comparator: LocalComparator | LLMComparator
    scorer: MatchScorer

    async def run(
        self,
        resume_bytes: bytes,
        resume_name: str,
        job_description: str,
        company_about: str = "",
    ) -> MatchResponse:
        started = time.perf_counter()

        resume_doc = self.pdf_parser.parse(resume_bytes, resume_name)
        job_doc = build_job_document(job_description, company_about)

        resume_vec, job_vec, comparison = await self._compare(resume_doc, job_doc)
        sim = cosine_similarity(resume_vec, job_vec)
        breakdown = self.scorer.score(sim, comparison)

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        provider = "openai" if self.settings.uses_openai else "free_local"
        return MatchResponse(
            overall_score=breakdown.overall_score,
            embedding_similarity=breakdown.embedding_similarity,
            llm_alignment_score=breakdown.llm_alignment_score,
            matched_skills=comparison.matched_skills,
            missing_skills=comparison.missing_skills,
            missing_requirements=comparison.missing_requirements,
            missing_qualifications=comparison.missing_qualifications,
            missing_experience=comparison.missing_experience,
            strengths=comparison.strengths,
            recommendations=comparison.recommendations,
            action_items=comparison.action_items,
            summary=comparison.summary,
            metadata={
                "resume_pages": resume_doc.page_count,
                "job_pages": job_doc.page_count,
                "resume_chars": resume_doc.char_count,
                "job_chars": job_doc.char_count,
                "job_input": "text",
                "match_provider": provider,
                "elapsed_ms": elapsed_ms,
                "embedding_model": (
                    self.settings.embedding_model
                    if self.settings.uses_openai
                    else "local-hash-embedder"
                ),
                "chat_model": (
                    self.settings.chat_model if self.settings.uses_openai else "local-rules"
                ),
            },
        )

    async def _compare(
        self, resume: ParsedDocument, job: ParsedDocument
    ):
        import asyncio

        resume_vec_task = asyncio.create_task(self.embedder.embed_document(resume.text))
        job_vec_task = asyncio.create_task(self.embedder.embed_document(job.text))
        comparison_task = asyncio.create_task(self.comparator.compare(resume, job))

        resume_vec, job_vec, comparison = await asyncio.gather(
            resume_vec_task, job_vec_task, comparison_task
        )
        return resume_vec, job_vec, comparison


def build_pipeline(settings: Settings) -> MatchPipeline:
    if settings.uses_openai:
        embedder: LocalEmbedder | OpenAIEmbedder = OpenAIEmbedder(settings)
        comparator: LocalComparator | LLMComparator = LLMComparator(settings)
    else:
        embedder = LocalEmbedder()
        comparator = LocalComparator()

    return MatchPipeline(
        settings=settings,
        pdf_parser=PyMuPDFParser(),
        embedder=embedder,
        comparator=comparator,
        scorer=MatchScorer(settings),
    )
