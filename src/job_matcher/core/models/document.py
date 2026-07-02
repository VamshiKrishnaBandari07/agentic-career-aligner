from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ParsedDocument:
    filename: str
    text: str
    page_count: int
    char_count: int
    parsed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
