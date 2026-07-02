from typing import Protocol

from job_matcher.core.models.document import ParsedDocument
from job_matcher.core.models.match_result import ComparisonResult


class SemanticComparator(Protocol):
    async def compare(
        self, resume: ParsedDocument, job: ParsedDocument
    ) -> ComparisonResult: ...
