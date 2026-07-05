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
from job_matcher.services.feedback.feedback_formatter import apply_feedback_limits

COMPARE_PROMPT = """You are a straight-talking career coach. Compare RESUME vs JOB DESCRIPTION.

Return ONLY valid JSON:
{{
  "llm_score": <0-100>,
  "missing_skills": [<skill/tool the job needs but resume lacks — max 6>],
  "missing_requirements": [<short gap, max 4>],
  "missing_qualifications": [<degree/years/certs gap, max 3>],
  "missing_experience": [<experience type missing, max 3>],
  "recommendations": [<top fixes, max 3>],
  "action_items": [<do this next, max 4>],
  "resume_suggestions": [<one-line CV edits, max 5>],
  "summary": <1-2 short sentences: fit level + what's missing. Do not list what already matches.>
}}

Voice & length (strict):
- Gaps only. Do not mention skills or experience the candidate already has.
- Write like a helpful human, not a report.
- Each string: ONE short sentence, under 20 words when possible.
- missing_skills: "Missing X." or "Missing X — add a bullet about Y."
- resume_suggestions: direct edit, e.g. "Add Docker to Skills if you've used it."
- Only list gaps you can see in the job text. Do not invent requirements.
- Skip empty categories. No filler, no repetition.
- summary: max 2 sentences. Focus on gaps and priority fixes only.

Scoring: 90+ excellent · 70-89 strong · 50-69 partial · below 50 weak

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
            data = apply_feedback_limits(json.loads(raw))
        except OpenAIError as exc:
            raise_comparison_error(exc)
        except Exception as exc:
            raise ComparisonError(f"OpenAI comparison failed: {exc}") from exc

        return ComparisonResult(
            llm_score=float(data.get("llm_score", 0)),
            matched_skills=[],
            missing_skills=_as_str_list(data.get("missing_skills")),
            missing_requirements=_as_str_list(data.get("missing_requirements")),
            missing_qualifications=_as_str_list(data.get("missing_qualifications")),
            missing_experience=_as_str_list(data.get("missing_experience")),
            strengths=[],
            recommendations=_as_str_list(data.get("recommendations")),
            action_items=_as_str_list(data.get("action_items")),
            resume_suggestions=_as_str_list(data.get("resume_suggestions")),
            summary=str(data.get("summary", "")),
        )
