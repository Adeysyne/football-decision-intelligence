from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = (
        "Football Decision Intelligence"
    )

    app_env: str = (
        "development"
    )

    app_version: str = (
        "0.1.0"
    )

    openai_api_key: str = ""

    openai_model: str = (
        "gpt-5.6-luna"
    )

    database_url: str = (
        "sqlite:///./"
        "football_decision_intelligence.db"
    )

    beta_access_code: str = ""

    admin_access_code: str = ""

    max_request_bytes: int = (
        65_536
    )

    api_rate_limit_per_minute: int = (
        180
    )

    ai_rate_limit_per_minute: int = (
        12
    )

    access_failure_limit: int = (
        8
    )

    access_failure_window_seconds: int = (
        300
    )

    security_enable_hsts: bool = (
        False
    )

    model_config = (
        SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()