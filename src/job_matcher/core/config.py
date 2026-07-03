from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _resolve_env_file() -> Path:
    candidates = [Path.cwd() / ".env", PROJECT_ROOT / ".env"]
    for path in candidates:
        if path.is_file():
            return path
    return PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_resolve_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    max_pdf_mb: int = 10
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_weight: float = 0.4
    llm_weight: float = 0.6

    @property
    def max_pdf_bytes(self) -> int:
        return self.max_pdf_mb * 1024 * 1024

    @property
    def openai_configured(self) -> bool:
        key = self.openai_api_key.strip()
        return bool(key) and key != "sk-your-key-here" and key.startswith("sk-")
