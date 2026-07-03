from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, InternalServerError, OpenAIError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from job_matcher.core.config import Settings
from job_matcher.integrations.openai.errors import raise_comparison_error


class OpenAIEmbeddings:
    def __init__(self, client: AsyncOpenAI, settings: Settings) -> None:
        self._client = client
        self._model = settings.embedding_model

    @retry(
        retry=retry_if_exception_type(
            (APIConnectionError, APITimeoutError, InternalServerError)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def create(self, texts: list[str]) -> list[list[float]]:
        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except OpenAIError as exc:
            raise_comparison_error(exc)
