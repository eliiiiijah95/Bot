"""Application configuration utilities."""
from __future__ import annotations

from functools import lru_cache
from typing import Iterable, Tuple

from pydantic import ValidationError
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic-based settings loaded from environment variables."""

    bot_token: SecretStr

    db_user: str
    db_pass: SecretStr
    db_host: str
    db_port: int
    db_name: str

    yookassa_account_id: str
    yookassa_secret_key: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def _format_missing_fields(locations: Iterable[Tuple[str, ...]]) -> str:
    return ", ".join(".".join(location) for location in locations)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance or raise a friendly error if secrets are missing."""

    try:
        return Settings()
    except ValidationError as exc:  # pragma: no cover - defensive guard
        missing_fields = [
            tuple(str(item) for item in error["loc"])
            for error in exc.errors()
            if error.get("type") == "missing"
        ]
        if missing_fields:
            hint = (
                "Создайте файл .env в корне проекта или задайте переменные окружения: "
                f"{_format_missing_fields(missing_fields)}."
            )
        else:
            hint = "Проверьте значения в .env и переменных окружения."
        raise RuntimeError(hint) from exc


settings = get_settings()
