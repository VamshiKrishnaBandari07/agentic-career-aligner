"""Trim and normalize feedback so responses stay short and readable."""

import re

# (field name, max items, max chars per item)
FEEDBACK_LIMITS: dict[str, tuple[int, int]] = {
    "matched_skills": (8, 50),
    "missing_skills": (6, 90),
    "missing_requirements": (4, 90),
    "missing_qualifications": (3, 80),
    "missing_experience": (3, 80),
    "strengths": (4, 80),
    "recommendations": (3, 90),
    "action_items": (4, 80),
    "resume_suggestions": (5, 110),
}

SUMMARY_MAX_CHARS = 220


def _trim_words(text: str, max_chars: int) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 1].rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "…"


def clamp_feedback_list(items: list[str], max_items: int, max_chars: int) -> list[str]:
    out: list[str] = []
    for item in items:
        if not item or not str(item).strip():
            continue
        cleaned = _trim_words(str(item), max_chars)
        if cleaned and cleaned not in out:
            out.append(cleaned)
        if len(out) >= max_items:
            break
    return out


def format_summary(text: str) -> str:
    return _trim_words(text, SUMMARY_MAX_CHARS)


def apply_feedback_limits(data: dict) -> dict:
    """Apply per-field limits to raw comparison dict from LLM or local builder."""
    for field, (max_items, max_chars) in FEEDBACK_LIMITS.items():
        raw = data.get(field)
        if isinstance(raw, list):
            data[field] = clamp_feedback_list(raw, max_items, max_chars)
    if data.get("summary"):
        data["summary"] = format_summary(str(data["summary"]))
    return data
