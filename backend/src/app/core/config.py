from functools import lru_cache
from typing import Literal, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Значение-заглушка для локальной разработки. В production запуск с ним запрещён.
_PLACEHOLDER_SECRET = "change-me"  # noqa: S105 — это не секрет, а маркер «не настроено»


class Settings(BaseSettings):
    """Настройки приложения. Читаются из переменных окружения и файла .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["local", "production"] = "local"
    database_url: str = "sqlite+aiosqlite:///./dosug.db"
    cors_origins: str = "http://localhost:5173"

    admin_username: str = "admin"
    admin_password: str = _PLACEHOLDER_SECRET
    secret_key: str = _PLACEHOLDER_SECRET

    @model_validator(mode="after")
    def _forbid_placeholder_secrets_in_production(self) -> Self:
        if self.app_env == "production" and _PLACEHOLDER_SECRET in {
            self.admin_password,
            self.secret_key,
        }:
            msg = "В production нужно задать ADMIN_PASSWORD и SECRET_KEY"
            raise ValueError(msg)
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
