SKILL_FIXES: dict[str, str] = {
    "Python": "Add one bullet with what you built and a number.",
    "FastAPI": "Mention an API you shipped — stack and scale.",
    "PyTorch": "Add a model you trained with dataset + metric.",
    "TensorFlow": "Name one ML project with results.",
    "Machine Learning": "One bullet: task, method, outcome.",
    "NLP": "Show text/LLM work — dataset or use case.",
    "Docker": "Say what you containerized and why.",
    "Kubernetes": "Note any deploy/orchestration experience.",
    "AWS": "List services you actually used.",
    "SQL": "Add a data/query win with impact.",
    "React": "One shipped UI or feature.",
    "Git": "Team workflow or OSS contribution.",
    "CI/CD": "Pipeline you ran or improved.",
    "LLM": "Prompting, fine-tune, or RAG example.",
    "RAG": "Retrieval setup you built or studied.",
}


def describe_missing_skill(skill: str, job_text: str) -> str:
    fix = SKILL_FIXES.get(skill, f"Add {skill} to Skills with a real example.")
    return f"Missing {skill}. {fix}"


def describe_missing_requirement(line: str) -> str:
    short = line.strip()[:70].rstrip()
    if len(line.strip()) > 70:
        short += "…"
    return f"Not on your CV: {short}. Add one bullet that proves it."


def describe_missing_qualification(gap: str) -> str:
    return f"{gap.strip()}. Add to Education or summary if you have it."


def describe_missing_experience(line: str) -> str:
    short = line.strip()[:65].rstrip()
    if len(line.strip()) > 65:
        short += "…"
    return f"Job wants: {short}. Tie a project or role to it."


def build_resume_suggestions(
    missing_skills: list[str],
    missing_requirements: list[str],
    missing_qualifications: list[str],
    missing_experience: list[str],
    job_text: str,
) -> list[str]:
    suggestions: list[str] = []

    if missing_skills:
        top = ", ".join(missing_skills[:3])
        suggestions.append(f"Skills line: add {top} if you have used them.")

    for skill in missing_skills[:3]:
        fix = SKILL_FIXES.get(skill, f"One bullet showing {skill} in practice.")
        suggestions.append(f"{skill}: {fix}")

    for req in missing_requirements[:2]:
        short = req[:60].rstrip() + ("…" if len(req) > 60 else "")
        suggestions.append(f"New bullet for: {short}")

    for qual in missing_qualifications[:1]:
        suggestions.append(f"Fix qualification gap: {qual[:75]}")

    for exp in missing_experience[:1]:
        suggestions.append(f"Reframe experience for: {exp[:65]}…")

    if not suggestions:
        suggestions.append("Add a Skills section and 2–3 quantified bullets, then retry.")

    return suggestions[:5]


def build_recommendations(
    missing_skills: list[str],
    missing_requirements: list[str],
    job_text: str,
) -> list[str]:
    recs: list[str] = []

    if missing_skills:
        recs.append(f"Focus first on: {', '.join(missing_skills[:4])}.")

    if missing_requirements:
        recs.append("One resume bullet per missing requirement.")

    if not recs:
        recs.append("Mirror keywords from the job in Summary and Skills.")

    return recs[:3]


def build_action_items(
    missing_skills: list[str],
    missing_qualifications: list[str],
) -> list[str]:
    items: list[str] = ["Tailor this CV to the job — save a copy per application."]

    for skill in missing_skills[:2]:
        items.append(f"Add {skill} to Skills + one proof bullet.")

    for qual in missing_qualifications[:1]:
        items.append(f"Address: {qual[:70]}")

    return items[:4]
