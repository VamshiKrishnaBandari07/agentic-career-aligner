from fastapi import Depends, Form

from job_matcher.core.config import Settings
from job_matcher.core.exceptions import EmptyTextError, OpenAINotConfiguredError
from job_matcher.core.pipeline.match_pipeline import MatchPipeline, build_pipeline
from job_matcher.services.pdf.pymupdf_parser import PyMuPDFParser


def get_settings() -> Settings:
    return Settings()


def get_pdf_parser() -> PyMuPDFParser:
    return PyMuPDFParser()


def require_job_description(job_description: str = Form(...)) -> str:
    text = job_description.strip()
    if not text:
        raise EmptyTextError("Paste the job description before analyzing.")
    return text


def get_pipeline(
    settings: Settings = Depends(get_settings),
    _job_description: str = Depends(require_job_description),
) -> MatchPipeline:
    if settings.uses_openai and not settings.openai_configured:
        raise OpenAINotConfiguredError(
            "OpenAI mode requires a valid API key. Set OPENAI_API_KEY in .env "
            "or switch MATCH_PROVIDER=free for no-cost local matching."
        )
    return build_pipeline(settings)
