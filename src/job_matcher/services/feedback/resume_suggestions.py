import re

from job_matcher.services.skills.skill_extractor import (
    extract_job_bullets,
    find_job_context,
    extract_skills,
)

# Resume-writing hints when a skill is missing from the CV
SKILL_RESUME_HINTS: dict[str, str] = {
    "Python": "Add a bullet quantifying Python work, e.g. 'Built [tool/pipeline] in Python processing [N] records/day, reducing [metric] by X%.'",
    "FastAPI": "Mention any REST API you built — framework name, endpoints, auth, and users/requests handled.",
    "PyTorch": "Describe a model you trained: dataset, architecture, metric (accuracy/F1), and deployment if any.",
    "TensorFlow": "Include a project bullet with model type, training data size, and evaluation results.",
    "Machine Learning": "Add 1–2 bullets with supervised/unsupervised tasks, algorithms used, and measurable outcomes.",
    "NLP": "Highlight tokenization, embeddings, transformers, or text classification with example datasets.",
    "Docker": "State what you containerized and how it improved deployment, reproducibility, or CI.",
    "Kubernetes": "Mention pods, services, or orchestration at any scale — even university/lab clusters count.",
    "AWS": "Name specific services (S3, Lambda, EC2, SageMaker) and what you built with them.",
    "SQL": "Quantify database work: tables, query optimization, or analytics that drove a decision.",
    "React": "Describe a UI you shipped: components, state management, and users or performance gains.",
    "Git": "Briefly note team workflow: branching strategy, PR reviews, or open-source contributions.",
    "CI/CD": "Explain the pipeline: tests run, deploy target, and frequency or reliability improvement.",
    "LLM": "Detail prompting, fine-tuning, RAG, or evaluation — include model names and use case.",
    "RAG": "Describe retrieval stack, chunking strategy, vector DB, and answer quality improvements.",
}


def describe_missing_skill(skill: str, job_text: str) -> str:
    context = find_job_context(job_text, skill)
    context_part = f" Job context: \"{context}\"" if context else ""
    hint = SKILL_RESUME_HINTS.get(
        skill,
        f"Add '{skill}' to your Skills section and support it with a project or work bullet that shows practical use.",
    )
    return (
        f"{skill} — Required by this role but not detected on your resume.{context_part} "
        f"Suggested change: {hint}"
    )


def describe_matched_skill(skill: str, job_text: str) -> str:
    context = find_job_context(job_text, skill)
    if context:
        return f"{skill} — Listed on your resume and required in the posting (\"{context[:100]}…\"). Emphasize this in your summary."
    return f"{skill} — Present on your resume and mentioned in the job description. Keep it prominent near the top."


def describe_missing_requirement(line: str) -> str:
    return (
        f"Gap: {line.strip()} — This requirement appears in the job description but is not clearly reflected "
        f"on your resume. Suggested change: Add a dedicated bullet under Experience or Projects that directly "
        f"addresses this, using action verbs (Built, Led, Delivered) and one measurable result."
    )


def describe_missing_qualification(gap: str) -> str:
    return (
        f"{gap} — Address in Education, Certifications, or a summary line. If you are close (e.g. MSc in progress), "
        f"state expected graduation date. If experience substitutes for years, map projects to equivalent years."
    )


def describe_missing_experience(line: str) -> str:
    return (
        f"Experience gap: {line.strip()} — The employer expects this background. Suggested change: Reframe relevant "
        f"internships, coursework, or personal projects using the same keywords from the job post, with metrics."
    )


def build_resume_suggestions(
    missing_skills: list[str],
    missing_requirements: list[str],
    missing_qualifications: list[str],
    missing_experience: list[str],
    job_text: str,
) -> list[str]:
    suggestions: list[str] = []

    suggestions.append(
        "Rewrite your professional summary in 3 lines: (1) role title you are targeting, "
        "(2) top 3 skills that match this job, (3) one standout achievement with a number."
    )

    for skill in missing_skills[:6]:
        hint = SKILL_RESUME_HINTS.get(skill, f"Mention {skill} with a concrete example.")
        suggestions.append(f"Skills section: add '{skill}'. {hint}")

    for req in missing_requirements[:4]:
        suggestions.append(
            f"New experience bullet: respond to — \"{req[:90]}…\" — Include tool used, scope, and outcome."
        )

    for qual in missing_qualifications[:3]:
        suggestions.append(f"Qualifications: {qual}. Add or clarify in Education/Certifications section.")

    for exp in missing_experience[:3]:
        suggestions.append(
            f"Reframe a past role or project to show: {exp[:80]}… Use the employer's exact phrasing where possible."
        )

    job_bullets = extract_job_bullets(job_text)
    if job_bullets:
        top = job_bullets[0][:100]
        suggestions.append(
            f"Mirror language from the posting. Example opening verb from job: \"{top}…\" — align 2–3 of your bullets similarly."
        )

    suggestions.append(
        "Quantify wherever possible: team size, dataset size, latency, accuracy, revenue, or time saved."
    )
    return suggestions[:12]


def build_recommendations(
    missing_skills: list[str],
    missing_requirements: list[str],
    matched_skills: list[str],
    job_text: str,
) -> list[str]:
    recs: list[str] = []

    if missing_skills:
        recs.append(
            f"Priority skills to surface: {', '.join(missing_skills[:5])}. "
            "Recruiters often scan Skills + first Experience block in under 30 seconds — put matches there."
        )

    if len(matched_skills) >= 3:
        recs.append(
            f"Lead with strengths: {', '.join(matched_skills[:4])}. "
            "Move the most relevant role or project to the top of Experience for this application."
        )

    if missing_requirements:
        recs.append(
            "Map each missing requirement to one resume bullet using the STAR format "
            "(Situation, Task, Action, Result) in 1–2 lines."
        )

    recs.append(
        "Tailor keywords from the job description into your resume naturally — especially in Summary, Skills, "
        "and the first bullet of each role. Avoid keyword stuffing; one strong example per skill is enough."
    )

    if "===" in job_text and "COMPANY" in job_text.upper():
        recs.append(
            "Reference the company's domain or values from the 'About the Company' section in your summary "
            "or cover letter to show cultural fit."
        )

    return recs[:8]


def build_action_items(
    missing_skills: list[str],
    missing_qualifications: list[str],
) -> list[str]:
    items: list[str] = [
        "Open the job description and highlight every 'required', 'must have', and 'preferred' phrase.",
        "For each highlight, add or edit one resume bullet that proves you meet it (or are actively learning it).",
    ]

    for skill in missing_skills[:4]:
        items.append(
            f"If you have used {skill}: add it to Skills + one bullet. If not: complete a small portfolio project "
            f"using {skill} this week and add that project."
        )

    for qual in missing_qualifications[:2]:
        items.append(f"Close qualification gap: {qual}")

    items.append("Ask a peer to read your updated resume against the job post — gaps you miss are often obvious to others.")
    items.append("Save this tailored version as Resume_[CompanyName]_[Role].pdf — never send a generic CV.")
    return items[:10]
