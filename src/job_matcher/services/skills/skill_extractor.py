import re

# Common technical skills for job/resume matching (case-insensitive)
SKILL_PATTERNS: list[tuple[str, str]] = [
    ("Python", r"\bpython\b"),
    ("Java", r"\bjava\b(?!\s*script)"),
    ("JavaScript", r"\b(javascript|js)\b"),
    ("TypeScript", r"\btypescript\b"),
    ("C++", r"\bc\+\+\b"),
    ("C#", r"\bc#\b"),
    ("Go", r"\b(golang|go)\b"),
    ("Rust", r"\brust\b"),
    ("SQL", r"\bsql\b"),
    ("NoSQL", r"\bnosql\b"),
    ("MongoDB", r"\bmongodb\b"),
    ("PostgreSQL", r"\b(postgresql|postgres)\b"),
    ("MySQL", r"\bmysql\b"),
    ("FastAPI", r"\bfastapi\b"),
    ("Django", r"\bdjango\b"),
    ("Flask", r"\bflask\b"),
    ("React", r"\breact\b"),
    ("Node.js", r"\bnode\.?js\b"),
    ("Vue", r"\bvue\.?js\b"),
    ("Angular", r"\bangular\b"),
    ("Docker", r"\bdocker\b"),
    ("Kubernetes", r"\b(kubernetes|k8s)\b"),
    ("AWS", r"\baws\b"),
    ("Azure", r"\bazure\b"),
    ("GCP", r"\b(gcp|google cloud)\b"),
    ("Machine Learning", r"\b(machine learning|ml)\b"),
    ("Deep Learning", r"\bdeep learning\b"),
    ("PyTorch", r"\bpytorch\b"),
    ("TensorFlow", r"\btensorflow\b"),
    ("NLP", r"\b(nlp|natural language processing)\b"),
    ("Computer Vision", r"\bcomputer vision\b"),
    ("LLM", r"\b(llm|large language model)\b"),
    ("OpenAI", r"\bopenai\b"),
    ("RAG", r"\brag\b"),
    ("Git", r"\bgit\b"),
    ("CI/CD", r"\bci/?cd\b"),
    ("REST API", r"\brest(\s+api)?\b"),
    ("GraphQL", r"\bgraphql\b"),
    ("Agile", r"\bagile\b"),
    ("Scrum", r"\bscrum\b"),
    ("Linux", r"\blinux\b"),
    ("Spark", r"\bspark\b"),
    ("Hadoop", r"\bhadoop\b"),
    ("Pandas", r"\bpandas\b"),
    ("NumPy", r"\bnumpy\b"),
    ("Scikit-learn", r"\bscikit[- ]?learn\b"),
    ("Power BI", r"\bpower bi\b"),
    ("Tableau", r"\btableau\b"),
    ("Excel", r"\bexcel\b"),
    ("Communication", r"\bcommunication skills?\b"),
    ("Leadership", r"\bleadership\b"),
    ("Teamwork", r"\bteam\s*work\b"),
]

DEGREE_PATTERNS: list[tuple[str, str]] = [
    ("PhD", r"\bph\.?d\b"),
    ("MSc", r"\b(msc|m\.sc|master'?s? degree)\b"),
    ("BSc", r"\b(bsc|b\.sc|bachelor'?s? degree)\b"),
    ("MBA", r"\bmba\b"),
]

EXPERIENCE_YEAR_PATTERN = re.compile(
    r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)",
    re.IGNORECASE,
)

REQUIREMENT_LINE_PATTERN = re.compile(
    r"(?:required|must have|should have|essential|mandatory|proficient in|experience with|knowledge of)",
    re.IGNORECASE,
)


def extract_skills(text: str) -> list[str]:
    found: list[str] = []
    lowered = text.lower()
    for name, pattern in SKILL_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE):
            found.append(name)
    return found


def extract_degrees(text: str) -> list[str]:
    found: list[str] = []
    for name, pattern in DEGREE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(name)
    return found


def extract_years_required(text: str) -> int | None:
    years: list[int] = []
    for match in EXPERIENCE_YEAR_PATTERN.finditer(text):
        years.append(int(match.group(1)))
    return max(years) if years else None


def extract_requirement_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip(" •-\t")
        if len(line) < 12:
            continue
        if REQUIREMENT_LINE_PATTERN.search(line):
            lines.append(line)
    return lines[:12]


def resume_years_hint(text: str) -> int | None:
    return extract_years_required(text)
