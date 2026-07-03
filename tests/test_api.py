import io

import pytest
from httpx import ASGITransport, AsyncClient

from job_matcher.main import app
from job_matcher.services.pdf.pymupdf_parser import PyMuPDFParser


@pytest.fixture
def sample_resume_pdf() -> bytes:
    return PyMuPDFParser.create_sample_pdf(
        "Jane Doe - Resume",
        "Skills: Python, FastAPI, Machine Learning, PyTorch, NLP. "
        "Experience: MSc AI student with 2 years Python development.",
    )


@pytest.fixture
def sample_job_pdf() -> bytes:
    return PyMuPDFParser.create_sample_pdf(
        "ML Engineer Job",
        "Requirements: Python, PyTorch, NLP, REST APIs, FastAPI. "
        "MSc in AI or related field preferred.",
    )


@pytest.mark.asyncio
async def test_home_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "Career Aligner" in response.text
    assert "Analyze Match" in response.text


@pytest.mark.asyncio
async def test_match_requires_openai_key(sample_resume_pdf: bytes, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("MATCH_PROVIDER", "openai")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/match",
            files={
                "resume": ("resume.pdf", io.BytesIO(sample_resume_pdf), "application/pdf"),
            },
            data={
                "job_description": "Requirements: Python, PyTorch, NLP, REST APIs, FastAPI.",
                "company_about": "AI startup focused on NLP products.",
            },
        )
    assert response.status_code == 503
    assert "OPENAI" in response.json()["detail"].upper()


@pytest.mark.asyncio
async def test_free_match_works_without_openai(
    sample_resume_pdf: bytes, sample_job_pdf: bytes, monkeypatch
):
    monkeypatch.setenv("MATCH_PROVIDER", "free")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/match",
            files={
                "resume": ("resume.pdf", io.BytesIO(sample_resume_pdf), "application/pdf"),
            },
            data={
                "job_description": "Requirements: Python, PyTorch, NLP, REST APIs, FastAPI.",
                "company_about": "AI startup focused on NLP products.",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["overall_score"] <= 100
    assert data["metadata"]["match_provider"] == "free_local"
    assert len(data["resume_suggestions"]) >= 1
    assert any("Python" in s for s in data["matched_skills"])
    assert len(data["missing_skills"][0]) > 20 if data["missing_skills"] else True


@pytest.mark.asyncio
async def test_match_requires_job_description_text(sample_resume_pdf: bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/match",
            files={
                "resume": ("resume.pdf", io.BytesIO(sample_resume_pdf), "application/pdf"),
            },
            data={"job_description": "   ", "company_about": ""},
        )
    assert response.status_code == 422
    assert "job description" in response.json()["detail"].lower()


def test_build_job_document_combines_company_and_description():
    from job_matcher.utils.text_document import build_job_document

    doc = build_job_document(
        job_description="Need Python and FastAPI.",
        company_about="We are a fintech company.",
    )
    assert "ABOUT THE COMPANY" in doc.text
    assert "fintech" in doc.text
    assert "JOB DESCRIPTION" in doc.text
    assert "Python" in doc.text


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "openai_configured" in data
    assert data["free_mode"] is True
    assert data["match_provider"] == "free"


@pytest.mark.asyncio
async def test_parse_pdf(sample_resume_pdf: bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/parse",
            files={"file": ("resume.pdf", io.BytesIO(sample_resume_pdf), "application/pdf")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["page_count"] >= 1
    assert "Python" in data["text_preview"]


def test_cosine_similarity_identical_vectors():
    from job_matcher.services.comparison.cosine_similarity import cosine_similarity

    vec = [1.0, 0.0, 0.0]
    assert cosine_similarity(vec, vec) == pytest.approx(1.0)


def test_chunk_text():
    from job_matcher.utils.chunking import chunk_text

    text = "a" * 2500
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    assert len(chunks) >= 2
