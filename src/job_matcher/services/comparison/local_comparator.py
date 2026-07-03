from job_matcher.core.models.document import ParsedDocument
from job_matcher.core.models.match_result import ComparisonResult
from job_matcher.services.analysis.gap_analyzer import analyze_resume_vs_job
from job_matcher.services.feedback.resume_suggestions import (
    build_action_items,
    build_recommendations,
    build_resume_suggestions,
    describe_matched_skill,
    describe_missing_experience,
    describe_missing_qualification,
    describe_missing_requirement,
    describe_missing_skill,
)


class LocalComparator:
    """Rule-based resume vs job comparison with detailed gap analysis."""

    async def compare(
        self, resume: ParsedDocument, job: ParsedDocument
    ) -> ComparisonResult:
        resume_text = resume.text
        job_text = job.text
        analysis = analyze_resume_vs_job(resume_text, job_text)

        matched_raw = analysis["matched_raw"]
        missing_raw = analysis["missing_raw"]

        matched_skills = [describe_matched_skill(s, job_text) for s in matched_raw]
        missing_skills = [describe_missing_skill(s, job_text) for s in missing_raw]

        missing_qualifications: list[str] = []
        for degree in sorted(analysis["job_degrees"] - analysis["resume_degrees"]):
            missing_qualifications.append(
                describe_missing_qualification(
                    f"Degree: {degree} — mentioned in job requirements but not found on resume"
                )
            )
        for cert in sorted(analysis["job_certs"] - analysis["resume_certs"]):
            missing_qualifications.append(
                describe_missing_qualification(
                    f"Certification: {cert} — preferred or required by employer"
                )
            )

        job_years = analysis["job_years"]
        resume_years = analysis["resume_years"]
        if job_years and (resume_years is None or resume_years < job_years):
            gap = (
                f"Experience: job requires ~{job_years}+ years"
                + (
                    f", resume suggests ~{resume_years} years"
                    if resume_years
                    else ", not stated on resume"
                )
            )
            missing_qualifications.append(describe_missing_qualification(gap))

        missing_requirements = [
            describe_missing_requirement(line) for line in analysis["missing_requirements"]
        ]
        missing_experience = [
            describe_missing_experience(line) for line in analysis["missing_experience"]
        ]

        strengths: list[str] = []
        if matched_raw:
            strengths.append(
                f"You align on {len(matched_raw)} skill(s)/keyword(s): {', '.join(matched_raw[:8])}"
                f"{'…' if len(matched_raw) > 8 else ''}. "
                "Keep these prominent in your summary and most recent role."
            )
        for req in analysis["covered_requirements"][:4]:
            strengths.append(
                f"Requirement covered: \"{req[:100]}{'…' if len(req) > 100 else ''}\" "
                "— already reflected on your resume."
            )
        if analysis["resume_degrees"] & analysis["job_degrees"]:
            strengths.append(
                f"Education match: {', '.join(sorted(analysis['resume_degrees'] & analysis['job_degrees']))}."
            )
        if analysis["extra_resume_skills"][:5]:
            strengths.append(
                f"Bonus skills on your resume (transferable): {', '.join(analysis['extra_resume_skills'][:5])}."
            )

        if analysis["resume_word_count"] < 25:
            strengths = [
                "⚠ Very little text was extracted from your resume PDF. "
                "Export a text-based PDF (not a scanned image) or add more content, then re-upload."
            ]

        missing_req_lines = analysis["missing_requirements"] + analysis["missing_experience"]
        recommendations = build_recommendations(
            missing_raw, missing_req_lines, matched_raw, job_text
        )
        action_items = build_action_items(missing_raw, missing_qualifications)
        resume_suggestions = build_resume_suggestions(
            missing_raw,
            missing_req_lines,
            missing_qualifications,
            missing_experience,
            job_text,
        )

        if not matched_raw and not missing_raw and analysis["job_word_count"] > 10:
            recommendations.insert(
                0,
                "Paste the full job description including Requirements and Responsibilities sections. "
                "Use bullet points or comma-separated skills for best detection.",
            )
            resume_suggestions.insert(
                0,
                "Ensure your resume PDF lists a Skills section and bullet points with technologies used "
                "(e.g. 'Built API in Python/FastAPI').",
            )

        total_job_signals = max(len(matched_raw) + len(missing_raw), 1)
        skill_score = len(matched_raw) / total_job_signals * 100
        gap_penalty = min(
            40,
            len(missing_raw) * 3
            + len(missing_requirements) * 2
            + len(missing_qualifications) * 3,
        )
        overlap_boost = analysis["text_overlap"] * 15
        llm_score = max(10.0, min(95.0, skill_score - gap_penalty + 25 + overlap_boost))

        gap_count = (
            len(missing_raw)
            + len(missing_requirements)
            + len(missing_qualifications)
            + len(missing_experience)
        )

        if llm_score >= 75:
            summary = (
                f"Strong fit — {len(matched_raw)} matches found, {gap_count} gap(s) to address. "
                f"Text overlap with the job posting: {int(analysis['text_overlap'] * 100)}%. "
                "Review suggested resume changes below."
            )
        elif llm_score >= 50:
            summary = (
                f"Moderate fit — {len(matched_raw)} matches, {gap_count} gap(s). "
                f"Overlap: {int(analysis['text_overlap'] * 100)}%. "
                "Each missing item below includes a specific fix for your resume."
            )
        else:
            summary = (
                f"Gaps detected — {len(matched_raw)} matches vs {gap_count} missing area(s). "
                f"Overlap: {int(analysis['text_overlap'] * 100)}%. "
                "Prioritize the missing skills and requirements sections below."
            )

        return ComparisonResult(
            llm_score=round(llm_score, 1),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            missing_requirements=missing_requirements,
            missing_qualifications=missing_qualifications,
            missing_experience=missing_experience,
            strengths=strengths
            or [
                "Add a Skills section and bullet-point experience to your resume for better analysis."
            ],
            recommendations=recommendations,
            action_items=action_items,
            resume_suggestions=resume_suggestions,
            summary=summary,
        )
