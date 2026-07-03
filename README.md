# Job Matcher

Modular Python backend that parses resume and job-description PDFs and performs semantic comparison using OpenAI embeddings and structured LLM analysis.

## Features

- PDF text extraction (PyMuPDF)
- OpenAI embeddings for semantic similarity
- GPT structured JSON comparison (skills gap, strengths, recommendations)
- Weighted final match score
- FastAPI with `/health`, `/parse`, and `/match` endpoints

## Quick start

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. Install package
pip install -e ".[dev]"

# 3. Configure OpenAI (required for /match)
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
# Edit .env and set OPENAI_API_KEY=sk-...

# 4. Run server
job-matcher
# or: uvicorn job_matcher.main:app --reload
```

Open **http://127.0.0.1:8000** — upload your resume PDF and job description PDF to get feedback.

API reference: **http://127.0.0.1:8000/docs**

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health + OpenAI config status |
| `/parse` | POST | Upload one PDF, get extracted text preview |
| `/match` | POST | Upload resume PDF + paste job description text → match analysis |

### Example: match two PDFs

```bash
curl -X POST "http://127.0.0.1:8000/match" ^
  -F "resume=@resume.pdf" ^
  -F "job_description=Python, FastAPI, ML required. 2+ years experience." ^
  -F "company_about=AI startup building NLP tools."
```

## Project structure

```
src/job_matcher/
├── api/              # FastAPI routes and dependency injection
├── core/             # Config, models, schemas, pipeline orchestration
├── services/         # PDF parsing, embedding, comparison, scoring
├── integrations/     # Thin OpenAI client wrappers
└── utils/            # Chunking, file validation
```

## Tests

```bash
pytest
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Required for `/match` |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHAT_MODEL` | `gpt-4o-mini` | Comparison model |
| `MAX_PDF_MB` | `10` | Max upload size per file |
| `EMBEDDING_WEIGHT` | `0.4` | Weight for embedding score |
| `LLM_WEIGHT` | `0.6` | Weight for LLM alignment score |

## License

MIT
