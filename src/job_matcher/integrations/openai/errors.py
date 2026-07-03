from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAIError,
    RateLimitError,
)

from job_matcher.core.exceptions import ComparisonError


def openai_error_message(exc: OpenAIError) -> str:
    if isinstance(exc, RateLimitError):
        code = _error_code(exc)
        if code == "insufficient_quota":
            return (
                "Your OpenAI account has no available quota. "
                "Add billing at https://platform.openai.com/account/billing "
                "and ensure your API key has credits, then try again."
            )
        return "OpenAI rate limit reached. Please wait a minute and try again."

    if isinstance(exc, AuthenticationError):
        return "Invalid OpenAI API key. Update OPENAI_API_KEY in your .env file."

    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return "Could not reach OpenAI. Check your internet connection and try again."

    return f"OpenAI API error: {exc}"


def _error_code(exc: OpenAIError) -> str | None:
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            code = error.get("code")
            if code:
                return str(code)

    message = str(exc).lower()
    if "insufficient_quota" in message or "exceeded your current quota" in message:
        return "insufficient_quota"
    return None


def raise_comparison_error(exc: OpenAIError) -> None:
    raise ComparisonError(openai_error_message(exc)) from exc
