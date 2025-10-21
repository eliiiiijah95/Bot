"""Application configuration loaded from environment variables or a .env file.

This module exposes a single ``config`` object that contains the runtime
settings for the bot.  It relies on :mod:`pydantic-settings` to validate and
parse values which keeps secrets (bot token, database password, etc.) out of the
source code while still allowing sensible defaults for local development.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Container for application settings.

    Environment variables (or values defined in a ``.env`` file) are mapped to
    the attributes below.  Only the Telegram bot token and database credentials
    are required; everything else is optional.
    """

    bot_token: SecretStr = Field(alias="BOT_TOKEN")

    # Optional payment-related settings
    provider_token: Optional[SecretStr] = Field(default=None, alias="PROVIDER_TOKEN")
    currency: Optional[str] = Field(default=None, alias="CURRENCY")

    # Database configuration
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")
    db_user: str = Field(alias="DB_USER")
    db_pass: SecretStr = Field(alias="DB_PASS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("db_host", mode="after")
    @classmethod
    def _ensure_db_host(cls, value: str) -> str:
        """Fallback to ``localhost`` when an empty host is provided.

        Users frequently leave ``DB_HOST`` blank when running the application
        locally.  SQLAlchemy/asyncpg then attempt to resolve an empty hostname
        which results in ``socket.gaierror``.  Normalising the value here keeps
        the configuration forgiving without masking real hostnames.
        """

        value = value.strip()
        return value or "localhost"

    def build_database_url(self) -> str:
        """Construct the SQLAlchemy database URL used by the application."""

        if self.database_url:
            return self.database_url

        password = self.db_pass.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def _get_settings() -> Settings:
    return Settings()


config = _get_settings()

__all__ = ["Settings", "config"]
