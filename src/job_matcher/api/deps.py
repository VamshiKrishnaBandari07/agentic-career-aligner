from functools import lru_cache

from fastapi import Depends

from job_matcher.core.config import Settings
from job_matcher.core.pipeline.match_pipeline import MatchPipeline, build_pipeline
from job_matcher.services.pdf.pymupdf_parser import PyMuPDFParser


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_pdf_parser() -> PyMuPDFParser:
    return PyMuPDFParser()


def get_pipeline(settings: Settings = Depends(get_settings)) -> MatchPipeline:
    return build_pipeline(settings)
