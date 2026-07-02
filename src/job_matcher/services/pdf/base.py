from typing import Protocol

from job_matcher.core.models.document import ParsedDocument


class PDFParser(Protocol):
    def parse(self, file_bytes: bytes, filename: str) -> ParsedDocument: ...
