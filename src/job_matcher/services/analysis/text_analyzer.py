import re

STOPWORDS = frozenset(
    """
    a an the and or but in on at to for of with by from as is are was were be been
    being have has had do does did will would shall should may might must can could
    this that these those it its we you they he she our your their not no yes all
    any each other such than then into over also about role job work team using use
    ability able strong excellent good well new help make made including include
    within across during per via etc through both either neither very more most
    some many much how what when where who which while during before after between
    """.split()
)

SKILLS_LINE_PATTERN = re.compile(
    r"(?:skills?|technical skills?|technologies?|tech stack|requirements?|qualifications?|must have)\s*[:\-]\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)

COMMA_SKILL_PATTERN = re.compile(
    r"\b([A-Z][a-zA-Z0-9+#.]*(?:\s+[A-Z][a-zA-Z0-9+#.]*){0,2})\b"
)


def content_words(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9+#.]{3,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def overlap_ratio(phrase: str, document: str) -> float:
    phrase_words = content_words(phrase)
    if not phrase_words:
        return 0.0
    doc_words = content_words(document)
    return len(phrase_words & doc_words) / len(phrase_words)


def resume_covers_phrase(resume_text: str, phrase: str, threshold: float = 0.38) -> bool:
    if not phrase.strip():
        return True
    if phrase.lower() in resume_text.lower():
        return True
  # Check significant substrings (4+ word chunks)
    words = phrase.split()
    if len(words) >= 3:
        chunk = " ".join(words[:4]).lower()
        if chunk in resume_text.lower():
            return True
    return overlap_ratio(phrase, resume_text) >= threshold


def extract_list_skills(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    for match in SKILLS_LINE_PATTERN.finditer(text):
        chunk = match.group(1).split("\n")[0]
        for part in re.split(r"[,;|/•·]", chunk):
            skill = _normalize_skill_token(part)
            if skill and skill.lower() not in seen:
                found.append(skill)
                seen.add(skill.lower())

    for line in text.splitlines():
        if "," in line and len(line) < 120:
            lower = line.lower()
            if any(k in lower for k in ("skill", "tech", "require", "stack", "proficien")):
                for part in line.split(":")[-1].split(","):
                    skill = _normalize_skill_token(part)
                    if skill and skill.lower() not in seen:
                        found.append(skill)
                        seen.add(skill.lower())

    return found


def _normalize_skill_token(raw: str) -> str:
    token = raw.strip(" .-•*()[]")
    if not token or len(token) < 2 or len(token) > 45:
        return ""
    if token.lower() in STOPWORDS:
        return ""
    if token.isdigit():
        return ""
    return token


def extract_job_phrases(text: str) -> list[str]:
    """Pull every meaningful line or sentence from the job posting."""
    phrases: list[str] = []
    seen: set[str] = set()

    job_body = text
    if "=== JOB DESCRIPTION ===" in text:
        job_body = text.split("=== JOB DESCRIPTION ===", 1)[-1]

    for raw in job_body.splitlines():
        line = raw.strip(" •-\t*0123456789.")
        if len(line) < 18 or line.lower() in seen:
            continue
        if line.startswith("==="):
            continue
        phrases.append(line)
        seen.add(line.lower())

    if len(phrases) < 4:
        for sentence in re.split(r"(?<=[.!?])\s+|[;\n]+", job_body):
            sentence = sentence.strip(" •-\t")
            if len(sentence) >= 25 and sentence.lower() not in seen:
                phrases.append(sentence)
                seen.add(sentence.lower())

    return phrases[:30]


def extract_top_job_keywords(job_text: str, resume_text: str, limit: int = 15) -> list[str]:
    """Keywords frequent in job but useful for gap detection."""
    job_words = content_words(job_text)
    resume_words = content_words(resume_text)
    job_freq: dict[str, int] = {}
    for word in re.findall(r"[a-z0-9+#.]{4,}", job_text.lower()):
        if word in STOPWORDS:
            continue
        job_freq[word] = job_freq.get(word, 0) + 1

    ranked = sorted(job_freq.items(), key=lambda x: (-x[1], x[0]))
    keywords: list[str] = []
    for word, _ in ranked:
        if word in resume_words:
            continue
        if len(keywords) >= limit:
            break
        keywords.append(word)
    return keywords


def merge_skill_sets(*skill_lists: list[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for skills in skill_lists:
        for skill in skills:
            key = skill.lower()
            if key not in seen:
                merged.append(skill)
                seen.add(key)
    return merged
