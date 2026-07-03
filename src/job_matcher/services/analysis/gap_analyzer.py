import re

from job_matcher.services.analysis.text_analyzer import (
    STOPWORDS,
    content_words,
    extract_job_phrases,
    extract_list_skills,
    extract_top_job_keywords,
    merge_skill_sets,
    overlap_ratio,
    resume_covers_phrase,
)
from job_matcher.services.skills.skill_extractor import (
    SKILL_PATTERNS,
    extract_certifications,
    extract_degrees,
    extract_requirement_lines,
    extract_skills,
    extract_years_required,
    find_job_context,
)

EXPERIENCE_KEYWORDS = (
    "experience",
    "years",
    "worked",
    "proven track",
    "demonstrated",
    "background in",
    "prior experience",
)

REQUIREMENT_HINT = re.compile(
    r"requir|must|should|proficien|experien|responsib|qualif|degree|bachelor|master|"
    r"develop|design|implement|knowledge|ability|familiar|understanding|preferred|essential",
    re.IGNORECASE,
)


def _skill_on_resume(skill: str, resume_text: str, resume_skills: list[str]) -> bool:
    skill_lower = skill.lower()
    if skill_lower in {s.lower() for s in resume_skills}:
        return True
    if re.search(rf"\b{re.escape(skill_lower)}\b", resume_text, re.IGNORECASE):
        return True
    for name, pattern in SKILL_PATTERNS:
        if name.lower() == skill_lower and re.search(pattern, resume_text, re.IGNORECASE):
            return True
    return False


def _is_requirement_like(phrase: str) -> bool:
    if REQUIREMENT_HINT.search(phrase):
        return True
    if extract_skills(phrase):
        return True
    if re.search(r"\b\d+\+?\s*years?", phrase, re.IGNORECASE):
        return True
    return len(phrase.split()) >= 6


def _is_valid_skill_name(skill: str) -> bool:
    if len(skill) > 45 or len(skill.split()) > 4:
        return False
    if skill.lower() in STOPWORDS:
        return False
    return True


def analyze_resume_vs_job(resume_text: str, job_text: str) -> dict:
    pattern_job = extract_skills(job_text)
    pattern_resume = extract_skills(resume_text)
    list_job = [s for s in extract_list_skills(job_text) if _is_valid_skill_name(s)]
    list_resume = [s for s in extract_list_skills(resume_text) if _is_valid_skill_name(s)]

    job_skill_names = merge_skill_sets(pattern_job, list_job)
    resume_skill_names = merge_skill_sets(pattern_resume, list_resume)

    matched_raw: list[str] = []
    missing_raw: list[str] = []
    seen_matched: set[str] = set()
    seen_missing: set[str] = set()

    for skill in job_skill_names:
        if _skill_on_resume(skill, resume_text, resume_skill_names):
            key = skill.lower()
            if key not in seen_matched:
                matched_raw.append(skill)
                seen_matched.add(key)
        else:
            key = skill.lower()
            if key not in seen_missing:
                missing_raw.append(skill)
                seen_missing.add(key)

    for skill in pattern_resume:
        if find_job_context(job_text, skill):
            key = skill.lower()
            if key not in seen_matched and key not in seen_missing:
                matched_raw.append(skill)
                seen_matched.add(key)

    extra_resume_skills = [
        s for s in resume_skill_names if s.lower() not in seen_matched
    ]

    missing_requirements: list[str] = []
    missing_experience: list[str] = []
    covered_requirements: list[str] = []

    candidate_phrases = merge_skill_sets(
        extract_requirement_lines(job_text),
        [p for p in extract_job_phrases(job_text) if _is_requirement_like(p)],
    )

    seen_phrases: set[str] = set()
    for phrase in candidate_phrases:
        key = phrase.lower()[:100]
        if key in seen_phrases:
            continue
        seen_phrases.add(key)

        if resume_covers_phrase(resume_text, phrase):
            covered_requirements.append(phrase)
            continue

        if any(kw in phrase.lower() for kw in EXPERIENCE_KEYWORDS):
            missing_experience.append(phrase)
        else:
            missing_requirements.append(phrase)

    if len(matched_raw) + len(missing_raw) < 3:
        for kw in extract_top_job_keywords(job_text, resume_text, limit=12):
            if resume_covers_phrase(resume_text, kw, threshold=0.5):
                if kw.lower() not in seen_matched:
                    matched_raw.append(kw.title())
                    seen_matched.add(kw.lower())
            elif kw.lower() not in seen_missing:
                missing_raw.append(kw.title())
                seen_missing.add(kw.lower())

    return {
        "matched_raw": matched_raw,
        "missing_raw": missing_raw,
        "extra_resume_skills": extra_resume_skills,
        "missing_requirements": missing_requirements[:12],
        "missing_experience": missing_experience[:10],
        "covered_requirements": covered_requirements[:15],
        "job_degrees": set(extract_degrees(job_text)),
        "resume_degrees": set(extract_degrees(resume_text)),
        "job_certs": set(extract_certifications(job_text)),
        "resume_certs": set(extract_certifications(resume_text)),
        "job_years": extract_years_required(job_text),
        "resume_years": extract_years_required(resume_text),
        "resume_word_count": len(content_words(resume_text)),
        "job_word_count": len(content_words(job_text)),
        "text_overlap": round(overlap_ratio(job_text, resume_text), 3),
    }
