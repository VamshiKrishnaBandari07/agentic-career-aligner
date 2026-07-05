from job_matcher.services.feedback.feedback_formatter import (
    apply_feedback_limits,
    clamp_feedback_list,
    format_summary,
)


def test_clamp_feedback_list_dedupes_and_limits():
    items = ["Short one.", "Short one.", "A" * 200]
    out = clamp_feedback_list(items, max_items=2, max_chars=50)
    assert len(out) == 2
    assert len(out[1]) <= 50


def test_apply_feedback_limits_caps_fields():
    data = apply_feedback_limits({
        "matched_skills": [f"skill-{i}" for i in range(20)],
        "resume_suggestions": ["x" * 300] * 10,
        "summary": "word " * 80,
    })
    assert len(data["matched_skills"]) <= 8
    assert len(data["resume_suggestions"]) <= 5
    assert len(data["summary"]) <= 220


def test_format_summary_trims_long_text():
    text = "This is a reasonable summary that should stay intact."
    assert format_summary(text) == text
