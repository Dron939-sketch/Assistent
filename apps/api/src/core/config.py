"""
Application configuration using Pydantic Settings.

Secrets (JWT_SECRET, REFRESH_TOKEN_SECRET, OPENAI_API_KEY) come from the
deployment environment (Render env vars). In production we fail loudly if any
of them are missing or left at the default placeholder.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator


PLACEHOLDER_SECRETS = {
    "change_me_in_production",
    "change_me_too",
    "change_this_to_random_string",
    "change_this_to_another_random_string",
    "",
}


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "FishFlow"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")  # development, staging, production

    # URLs
    APP_URL: str = Field(default="http://localhost:3000")
    API_URL: str = Field(default="http://localhost:8000")

    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/fishflow")
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=40)

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")
    REDIS_PASSWORD: Optional[str] = None

    # Auth — must be supplied via env in non-development environments
    JWT_SECRET: str = Field(default="change_me_in_production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRES_IN: int = Field(default=7)  # days
    REFRESH_TOKEN_SECRET: str = Field(default="change_me_too")

    # VK API
    VK_APP_ID: int = Field(default=0)
    VK_APP_SECRET: str = Field(default="")
    VK_SERVICE_KEY: str = Field(default="")
    VK_CALLBACK_SECRET: str = Field(default="")
    VK_API_VERSION: str = Field(default="5.199")

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None

    # AI / LLM
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview")
    OPENAI_TEMPERATURE: float = Field(default=0.7)
    OPENAI_MAX_TOKENS: int = Field(default=2000)

    # YandexGPT (optional, for Russian-specific)
    YANDEX_GPT_API_KEY: Optional[str] = None
    YANDEX_GPT_FOLDER_ID: Optional[str] = None

    # Payments
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_START_PRICE_ID: Optional[str] = None
    STRIPE_PRO_PRICE_ID: Optional[str] = None
    STRIPE_EXPERT_PRICE_ID: Optional[str] = None

    # Email
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_FROM: str = Field(default="noreply@fishflow.com")

    # Storage
    S3_ENDPOINT: Optional[str] = None
    S3_BUCKET: str = Field(default="fishflow-assets")
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None

    # CORS — list explicit origins (no wildcards). Configure via CORS_ORIGINS env.
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "https://app.fishflow.ru",
            "https://fishflow.ru",
        ]
    )

    # Security
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "*.fishflow.ru", "fishflow.ru"])

    # Tenant
    DEFAULT_TENANT: str = Field(default="nutrition")

    # Rate limiting
    RATE_LIMIT_WINDOW_MS: int = Field(default=60000)
    RATE_LIMIT_MAX_REQUESTS: int = Field(default=100)

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    @model_validator(mode="after")
    def _enforce_production_secrets(self) -> "Settings":
        if self.ENVIRONMENT.lower() in {"production", "prod", "staging"}:
            problems: List[str] = []
            if self.JWT_SECRET in PLACEHOLDER_SECRETS:
                problems.append("JWT_SECRET")
            if self.REFRESH_TOKEN_SECRET in PLACEHOLDER_SECRETS:
                problems.append("REFRESH_TOKEN_SECRET")
            if not self.OPENAI_API_KEY:
                problems.append("OPENAI_API_KEY")
            if problems:
                raise ValueError(
                    "Missing or placeholder secrets in "
                    f"{self.ENVIRONMENT}: {', '.join(problems)}. "
                    "Set them via environment variables."
                )
        return self


# Singleton instance
settings = Settings()
