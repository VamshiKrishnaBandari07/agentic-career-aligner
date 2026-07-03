class JobMatcherError(Exception):
    """Base domain error."""


class PDFParseError(JobMatcherError):
    """Failed to extract text from a PDF."""


class EmptyTextError(JobMatcherError):
    """Required text input is missing or empty."""


class FileTooLargeError(JobMatcherError):
    """Uploaded file exceeds configured limit."""


class OpenAINotConfiguredError(JobMatcherError):
    """OpenAI API key is missing or placeholder."""


class ComparisonError(JobMatcherError):
    """Semantic comparison failed."""
