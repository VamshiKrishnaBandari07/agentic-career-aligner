from functools import lru_cache

from fastapi import Depends, Form

from job_matcher.core.config import Settings
from job_matcher.core.exceptions import EmptyTextError, OpenAINotConfiguredError
from job_matcher.core.pipeline.match_pipeline import MatchPipeline, build_pipeline
from job_matcher.services.pdf.pymupdf_parser import PyMuPDFParser


@lru_cache
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
    if not settings.openai_configured:
        raise OpenAINotConfiguredError(
            "Set OPENAI_API_KEY in .env before calling /match"
        )
    return build_pipeline(settings)
