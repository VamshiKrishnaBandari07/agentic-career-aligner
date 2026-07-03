import json

from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    InternalServerError,
    OpenAIError,
)
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from job_matcher.core.config import Settings
from job_matcher.core.exceptions import ComparisonError
from job_matcher.core.models.document import ParsedDocument
from job_matcher.core.models.match_result import ComparisonResult
from job_matcher.integrations.openai.errors import raise_comparison_error

COMPARE_PROMPT = """You are an expert career coach and technical recruiter.
Compare the candidate's RESUME against the JOB DESCRIPTION.

Return ONLY valid JSON with this exact schema:
{{
  "llm_score": <number 0-100>,
  "matched_skills": [<skills the resume clearly demonstrates that the job wants>],
  "missing_skills": [<technical skills, tools, or technologies required by the job but absent or weak on resume>],
  "missing_requirements": [<non-skill requirements missing: responsibilities, methodologies, soft requirements, domain knowledge>],
  "missing_qualifications": [<education, degree level, certifications, minimum years of experience not met>],
  "missing_experience": [<specific work experience types, projects, or achievements the job expects but resume lacks>],
  "strengths": [<what makes this candidate a good fit>],
  "recommendations": [<resume improvements tailored to this specific job>],
  "action_items": [<3-6 concrete steps the candidate should take to improve their fit>],
  "summary": <2-3 sentences explaining overall fit in encouraging but honest language>
}}

Rules:
- Be specific. Quote or paraphrase actual requirements from the job description.
- List every meaningful gap you find — do not leave arrays empty if gaps exist.
- Distinguish skills (e.g. Python, AWS) from requirements (e.g. agile teamwork) from qualifications (e.g. MSc required).
- action_items must be actionable (e.g. "Add a bullet about your NLP capstone project metrics").

Scoring guide:
- 90-100: Excellent fit
- 70-89: Strong fit, minor gaps
- 50-69: Partial fit, notable gaps
- Below 50: Weak fit

RESUME:
{resume}

JOB DESCRIPTION:
{job}
"""


def _as_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item]


class OpenAIChat:
    def __init__(self, client: AsyncOpenAI, settings: Settings) -> None:
        self._client = client
        self._model = settings.chat_model

    @retry(
        retry=retry_if_exception_type(
            (APIConnectionError, APITimeoutError, InternalServerError)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def compare_documents(
        self, resume: ParsedDocument, job: ParsedDocument
    ) -> ComparisonResult:
        prompt = COMPARE_PROMPT.format(
            resume=resume.text[:12000],
            job=job.text[:12000],
        )
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "You output strict JSON only. No markdown fences.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)
        except OpenAIError as exc:
            raise_comparison_error(exc)
        except Exception as exc:
            raise ComparisonError(f"OpenAI comparison failed: {exc}") from exc

        return ComparisonResult(
            llm_score=float(data.get("llm_score", 0)),
            matched_skills=_as_str_list(data.get("matched_skills")),
            missing_skills=_as_str_list(data.get("missing_skills")),
            missing_requirements=_as_str_list(data.get("missing_requirements")),
            missing_qualifications=_as_str_list(data.get("missing_qualifications")),
            missing_experience=_as_str_list(data.get("missing_experience")),
            strengths=_as_str_list(data.get("strengths")),
            recommendations=_as_str_list(data.get("recommendations")),
            action_items=_as_str_list(data.get("action_items")),
            summary=str(data.get("summary", "")),
        )
