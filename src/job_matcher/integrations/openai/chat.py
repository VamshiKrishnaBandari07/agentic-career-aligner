import json

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from job_matcher.core.config import Settings
from job_matcher.core.exceptions import ComparisonError
from job_matcher.core.models.document import ParsedDocument
from job_matcher.core.models.match_result import ComparisonResult

COMPARE_PROMPT = """You are an expert technical recruiter. Compare the resume against the job description.

Return ONLY valid JSON with this exact schema:
{
  "llm_score": <number 0-100>,
  "matched_skills": [<strings>],
  "missing_skills": [<strings>],
  "strengths": [<strings>],
  "recommendations": [<strings>],
  "summary": <one paragraph string>
}

Scoring guide:
- 90-100: Excellent fit, most requirements clearly met
- 70-89: Strong fit with minor gaps
- 50-69: Partial fit, notable gaps
- Below 50: Weak fit

RESUME:
{resume}

JOB DESCRIPTION:
{job}
"""


class OpenAIChat:
    def __init__(self, client: AsyncOpenAI, settings: Settings) -> None:
        self._client = client
        self._model = settings.chat_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
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
        except Exception as exc:
            raise ComparisonError(f"OpenAI comparison failed: {exc}") from exc

        return ComparisonResult(
            llm_score=float(data.get("llm_score", 0)),
            matched_skills=list(data.get("matched_skills", [])),
            missing_skills=list(data.get("missing_skills", [])),
            strengths=list(data.get("strengths", [])),
            recommendations=list(data.get("recommendations", [])),
            summary=str(data.get("summary", "")),
        )
