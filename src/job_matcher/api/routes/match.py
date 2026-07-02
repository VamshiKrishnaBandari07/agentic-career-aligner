from fastapi import APIRouter, Depends, File, UploadFile

from job_matcher.api.deps import get_pdf_parser, get_pipeline, get_settings
from job_matcher.core.config import Settings
from job_matcher.core.exceptions import OpenAINotConfiguredError
from job_matcher.core.pipeline.match_pipeline import MatchPipeline
from job_matcher.core.schemas.match import MatchResponse, ParseResponse
from job_matcher.services.pdf.pymupdf_parser import PyMuPDFParser
from job_matcher.utils.file_io import validate_file_size

router = APIRouter(tags=["documents"])


async def _read_upload(upload: UploadFile, settings: Settings) -> tuple[bytes, str]:
    data = await upload.read()
    filename = upload.filename or "document.pdf"
    validate_file_size(data, settings.max_pdf_bytes, filename)
    return data, filename


@router.post("/parse", response_model=ParseResponse)
async def parse_pdf(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    parser: PyMuPDFParser = Depends(get_pdf_parser),
) -> ParseResponse:
    data, filename = await _read_upload(file, settings)
    doc = parser.parse(data, filename)
    preview = doc.text[:500]
    return ParseResponse(
        filename=doc.filename,
        page_count=doc.page_count,
        char_count=doc.char_count,
        text_preview=preview,
    )


@router.post("/match", response_model=MatchResponse)
async def match_documents(
    resume: UploadFile = File(..., description="Resume PDF"),
    job_description: UploadFile = File(..., description="Job description PDF"),
    settings: Settings = Depends(get_settings),
    pipeline: MatchPipeline = Depends(get_pipeline),
) -> MatchResponse:
    if not settings.openai_configured:
        raise OpenAINotConfiguredError(
            "Set OPENAI_API_KEY in .env before calling /match"
        )

    resume_bytes, resume_name = await _read_upload(resume, settings)
    job_bytes, job_name = await _read_upload(job_description, settings)
    return await pipeline.run(resume_bytes, resume_name, job_bytes, job_name)
