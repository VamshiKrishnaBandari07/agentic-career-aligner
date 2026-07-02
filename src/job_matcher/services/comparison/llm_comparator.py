from job_matcher.core.config import Settings
from job_matcher.core.models.document import ParsedDocument
from job_matcher.core.models.match_result import ComparisonResult
from job_matcher.integrations.openai.chat import OpenAIChat
from job_matcher.integrations.openai.client import create_openai_client


class LLMComparator:
    def __init__(self, settings: Settings) -> None:
        client = create_openai_client(settings)
        self._chat = OpenAIChat(client, settings)

    async def compare(
        self, resume: ParsedDocument, job: ParsedDocument
    ) -> ComparisonResult:
        return await self._chat.compare_documents(resume, job)
