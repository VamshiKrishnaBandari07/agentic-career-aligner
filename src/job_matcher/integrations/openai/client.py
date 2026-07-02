from openai import AsyncOpenAI

from job_matcher.core.config import Settings


def create_openai_client(settings: Settings) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)
