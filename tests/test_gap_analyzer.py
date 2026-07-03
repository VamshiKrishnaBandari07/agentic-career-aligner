from job_matcher.services.analysis.gap_analyzer import analyze_resume_vs_job


def test_analyze_finds_skills_in_pasted_job():
    resume = """
    John Doe — MSc AI Student
    Skills: Python, FastAPI, Machine Learning, PyTorch, NLP, Git
    Experience: Built a sentiment analysis API in Python/FastAPI for 10k reviews.
    Education: MSc Artificial Intelligence
    """
    job = """
    ML Engineer Role
    Requirements:
    - Strong Python and PyTorch experience
    - Experience with NLP and REST APIs
    - FastAPI or Django for backend services
    - 2+ years of machine learning experience preferred
    - MSc in AI or related field
      Skills: Python, PyTorch, NLP, Docker, Kubernetes, AWS
    """
    result = analyze_resume_vs_job(resume, job)
    assert "Python" in result["matched_raw"]
    assert any(
        m in result["missing_raw"] for m in ("Docker", "Kubernetes", "AWS")
    )
    assert len(result["matched_raw"]) >= 3


def test_analyze_detects_missing_requirements():
    resume = "Software developer with Java experience."
    job = """
    Responsibilities:
    - Design and deploy machine learning models in production
    - Collaborate with cross-functional teams using Agile methodology
    Must have experience with cloud platforms and MLOps pipelines.
    """
    result = analyze_resume_vs_job(resume, job)
    assert result["missing_raw"] or result["missing_requirements"] or result["missing_experience"]
