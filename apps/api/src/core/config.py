"""
Application configuration using Pydantic Settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
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
    
    # Auth
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
    
    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "https://*.fishflow.ru"])
    
    # Security
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "*.fishflow.ru"])
    
    # Rate limiting
    RATE_LIMIT_WINDOW_MS: int = Field(default=60000)
    RATE_LIMIT_MAX_REQUESTS: int = Field(default=100)
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()
