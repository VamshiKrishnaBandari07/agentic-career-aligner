from job_matcher.core.models.document import ParsedDocument
from job_matcher.core.models.match_result import ComparisonResult
from job_matcher.services.skills.skill_extractor import (
    extract_degrees,
    extract_requirement_lines,
    extract_skills,
    extract_years_required,
    resume_years_hint,
)


class LocalComparator:
    """Rule-based resume vs job comparison — free, runs locally."""

    async def compare(
        self, resume: ParsedDocument, job: ParsedDocument
    ) -> ComparisonResult:
        resume_skills = set(extract_skills(resume.text))
        job_skills = set(extract_skills(job.text))

        matched_skills = sorted(job_skills & resume_skills)
        missing_skills = sorted(job_skills - resume_skills)

        job_degrees = set(extract_degrees(job.text))
        resume_degrees = set(extract_degrees(resume.text))
        missing_qualifications = sorted(job_degrees - resume_degrees)

        job_years = extract_years_required(job.text)
        resume_years = resume_years_hint(resume.text)
        if job_years and (resume_years is None or resume_years < job_years):
            missing_qualifications.append(
                f"Job asks for {job_years}+ years experience"
                + (f" (resume shows ~{resume_years} yrs)" if resume_years else "")
            )

        missing_requirements: list[str] = []
        missing_experience: list[str] = []
        resume_lower = resume.text.lower()

        for line in extract_requirement_lines(job.text):
            key = _line_keywords(line)
            if not key:
                continue
            if key in resume_lower:
                continue
            bucket = missing_experience if "experience" in line.lower() else missing_requirements
            if line not in bucket:
                bucket.append(line)

        strengths: list[str] = []
        if matched_skills:
            strengths.append(
                f"Resume demonstrates {len(matched_skills)} job-relevant skills: "
                + ", ".join(matched_skills[:6])
                + ("…" if len(matched_skills) > 6 else "")
            )
        if resume_degrees & job_degrees:
            strengths.append(
                f"Education alignment: {', '.join(sorted(resume_degrees & job_degrees))}"
            )

        recommendations: list[str] = []
        action_items: list[str] = []

        for skill in missing_skills[:8]:
            recommendations.append(f"Add {skill} to your skills section if you have experience with it.")
            action_items.append(f"Highlight a project or coursework that used {skill}.")

        for req in missing_requirements[:4]:
            recommendations.append(f"Address this job requirement on your resume: {req[:120]}")
            action_items.append(f"Add a bullet point covering: {req[:80]}…")

        if not recommendations:
            recommendations.append("Tailor your summary to mirror the job title and top requirements.")

        if not action_items:
            action_items.append("Quantify achievements (metrics, impact) for your top 3 resume bullets.")

        skill_score = (len(matched_skills) / len(job_skills) * 100) if job_skills else 55.0
        gap_penalty = min(35, len(missing_skills) * 4 + len(missing_requirements) * 2)
        llm_score = max(15.0, min(95.0, skill_score - gap_penalty + 20))

        if llm_score >= 75:
            summary = (
                "Strong alignment on core skills. Focus on tailoring bullets to the exact role "
                "and filling any remaining gaps below."
            )
        elif llm_score >= 50:
            summary = (
                "Partial fit — you match some requirements but have notable gaps. "
                "Use the missing items below to improve your resume for this role."
            )
        else:
            summary = (
                "Limited overlap with this job posting. Consider upskilling in the missing areas "
                "or targeting roles that better match your current profile."
            )

        return ComparisonResult(
            llm_score=round(llm_score, 1),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            missing_requirements=missing_requirements,
            missing_qualifications=missing_qualifications,
            missing_experience=missing_experience,
            strengths=strengths or ["Review matched skills and expand relevant project details."],
            recommendations=recommendations[:8],
            action_items=action_items[:6],
            summary=summary,
        )


def _line_keywords(line: str) -> str:
    cleaned = line.lower()
    for prefix in ("required:", "must have:", "-", "•"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()
    return cleaned[:80]
