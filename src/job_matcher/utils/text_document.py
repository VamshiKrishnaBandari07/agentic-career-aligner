from datetime import datetime, timezone

from job_matcher.core.models.document import ParsedDocument


def text_to_document(
    text: str,
    filename: str,
    *,
    label: str = "",
) -> ParsedDocument:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError(f"{label or 'Text'} cannot be empty")

    return ParsedDocument(
        filename=filename,
        text=cleaned,
        page_count=1,
        char_count=len(cleaned),
        parsed_at=datetime.now(timezone.utc),
    )


def build_job_document(job_description: str, company_about: str = "") -> ParsedDocument:
    parts: list[str] = []
    company = company_about.strip()
    description = job_description.strip()

    if not description:
        raise ValueError("Job description cannot be empty")

    if company:
        parts.append("=== ABOUT THE COMPANY ===")
        parts.append(company)
        parts.append("")

    parts.append("=== JOB DESCRIPTION ===")
    parts.append(description)

    combined = "\n".join(parts)
    return ParsedDocument(
        filename="job_description.txt",
        text=combined,
        page_count=1,
        char_count=len(combined),
        parsed_at=datetime.now(timezone.utc),
    )
