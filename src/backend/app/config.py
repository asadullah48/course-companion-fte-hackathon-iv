"""
Application Configuration
Zero-Backend-LLM Architecture - No LLM settings allowed
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown env vars
    )

    # Application
    app_name: str = "course-companion"
    app_env: str = "development"
    environment: str = "development"  # Alias for app_env
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # Database (Railway provides DATABASE_URL without +asyncpg)
    database_url: str = "postgresql+asyncpg://localhost/course_companion"

    @property
    def async_database_url(self) -> str:
        """Get database URL with asyncpg driver for async SQLAlchemy."""
        url = self.database_url
        # Railway/Heroku provide postgresql:// but we need postgresql+asyncpg://
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    # Cloudflare R2 - Support both naming conventions
    r2_endpoint: str = ""
    r2_account_id: str = ""  # Alias
    r2_access_key: str = ""
    r2_access_key_id: str = ""  # Alias
    r2_secret_key: str = ""
    r2_secret_access_key: str = ""  # Alias
    r2_bucket_name: str = "course-content"

    # Redis (optional caching)
    redis_url: str | None = None

    # JWT Authentication
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "https://chat.openai.com"]

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Content Settings
    free_chapter_limit: int = 3  # First 3 chapters are free


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
