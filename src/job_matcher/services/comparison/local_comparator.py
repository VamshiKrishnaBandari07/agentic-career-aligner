from job_matcher.core.models.document import ParsedDocument
from job_matcher.core.models.match_result import ComparisonResult
from job_matcher.services.analysis.gap_analyzer import analyze_resume_vs_job
from job_matcher.services.feedback.feedback_formatter import apply_feedback_limits
from job_matcher.services.feedback.resume_suggestions import (
    build_action_items,
    build_recommendations,
    build_resume_suggestions,
    describe_missing_skill,
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

        if analysis["resume_word_count"] < 25:
            missing_skills.insert(
                0,
                "Resume text too short to read — use a text PDF, not a scan.",
            )

        missing_req_lines = analysis["missing_requirements"] + analysis["missing_experience"]
        recommendations = build_recommendations(
            missing_raw, missing_req_lines, job_text
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
                "Paste full Requirements and Responsibilities for better matching.",
            )
            resume_suggestions.insert(
                0,
                "Add a Skills section with tools you have used.",
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
            summary = f"Mostly there — fix {gap_count} gap(s) below."
        elif llm_score >= 50:
            summary = f"Some gaps — {gap_count} thing(s) to address before applying."
        else:
            summary = f"Several gaps — start with missing skills below."

        payload = apply_feedback_limits({
            "matched_skills": [],
            "missing_skills": missing_skills,
            "missing_requirements": missing_requirements,
            "missing_qualifications": missing_qualifications,
            "missing_experience": missing_experience,
            "strengths": [],
            "recommendations": recommendations,
            "action_items": action_items,
            "resume_suggestions": resume_suggestions,
            "summary": summary,
        })

        return ComparisonResult(
            llm_score=round(llm_score, 1),
            matched_skills=payload["matched_skills"],
            missing_skills=payload["missing_skills"],
            missing_requirements=payload["missing_requirements"],
            missing_qualifications=payload["missing_qualifications"],
            missing_experience=payload["missing_experience"],
            strengths=payload["strengths"],
            recommendations=payload["recommendations"],
            action_items=payload["action_items"],
            resume_suggestions=payload["resume_suggestions"],
            summary=payload["summary"],
        )
