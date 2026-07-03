# Career Aligner

> **I built this for my own job hunt. Now it's yours — free, local, no subscription.**

Upload your CV. Paste a job description. Get detailed feedback on fit, missing skills, and exactly what to change on your resume.

**No API key · No billing · No account · Your CV stays on your machine**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776ab?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/VamshiKrishnaBandari07/agentic-career-aligner/actions/workflows/ci.yml/badge.svg)](https://github.com/VamshiKrishnaBandari07/agentic-career-aligner/actions)

<p align="center">
  <strong>Clone → Run → Review your CV in 2 minutes</strong>
</p>

---

## One-command start

### Windows
```bat
git clone https://github.com/VamshiKrishnaBandari07/agentic-career-aligner.git
cd agentic-career-aligner
run.bat
```
Or double-click **`run.bat`**

### Mac / Linux
```bash
git clone https://github.com/VamshiKrishnaBandari07/agentic-career-aligner.git
cd agentic-career-aligner
chmod +x run.sh && ./run.sh
```

Open **http://127.0.0.1:8000** → upload resume → paste job → **Analyze Match**

---

## What you get

| Output | What it tells you |
|--------|-------------------|
| **Match score** | How well your CV fits this specific job (0–100%) |
| **Matched skills** | Skills you have that the job wants |
| **Missing skills** | Technical gaps + how to fix them on your CV |
| **Missing requirements** | Responsibilities not covered on your resume |
| **Missing qualifications** | Education / experience gaps |
| **Resume suggestions** | Exact bullets and sections to add |
| **Action items** | Step-by-step plan before you apply |

---

## Why I built this

Job hunting as an MSc AI student means tailoring your CV for every application. Paid resume tools charge monthly fees for the same analysis. I wanted something that:

- Works **offline on my laptop**
- Costs **nothing**
- Keeps my **CV private**
- Gives **actionable** feedback, not generic advice

So I built Career Aligner. I use it for every application. Now you can too.

---

## How it works

```
Resume PDF  ──►  PyMuPDF text extraction
                        │
Job text    ──►  Skill & requirement analysis  ──►  Gap report + suggestions
(pasted)            (runs locally, no cloud)
```

**Default mode = 100% free local analysis.** Optional OpenAI mode available if you want GPT-powered feedback (requires your own API key).

---

## Features

- PDF resume upload with smart text extraction
- Paste job description + optional company info
- Detailed gap analysis with resume rewrite suggestions
- Clean web UI — no install beyond Python
- REST API with Swagger docs at `/docs`
- Modular Python architecture (great for portfolios)
- CI tests on every push

---

## Manual setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -e .
job-matcher
```

No `.env` file needed. Free mode works out of the box.

---

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/match` | POST | Resume PDF + job text → full analysis |
| `/health` | GET | Status check |
| `/docs` | GET | Swagger API docs |

---

## Project structure

```
src/job_matcher/
├── api/              # FastAPI routes
├── core/             # Config, pipeline, schemas
├── services/
│   ├── analysis/     # Gap analyzer
│   ├── comparison/   # Local + optional OpenAI
│   ├── feedback/     # Resume suggestion builder
│   ├── pdf/          # PDF parser
│   └── skills/       # Skill extraction
├── integrations/     # Optional OpenAI client
└── static/           # Web UI
```

---

## Tests

```bash
pip install -e ".[dev]"
pytest
```

---

## LinkedIn post ready

See **[LINKEDIN.md](LINKEDIN.md)** for copy-paste posts to share this project.

---

## Tech stack

Python 3.10+ · FastAPI · PyMuPDF · NumPy · Pydantic · Uvicorn

---

## Author

**Vamshi Krishna Bandari** — MSc AI student  
[GitHub](https://github.com/VamshiKrishnaBandari07) · [Repository](https://github.com/VamshiKrishnaBandari07/agentic-career-aligner)

---

## License

MIT — use it, fork it, share it. See [LICENSE](LICENSE).
