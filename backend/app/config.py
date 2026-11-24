"""
Application Configuration Module.

Uses pydantic-settings for robust, validated environment management.
Supports .env files, type safety, and clean separation between environments.
"""

from pathlib import Path
from typing import List, Set
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base project paths
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
ENV_FILE = BACKEND_DIR / ".env"

class Settings(BaseSettings):
    """
    Central settings class validated via Pydantic.
    Values can be overridden by environment variables or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General
    ENVIRONMENT: str = Field(default="development", description="Current runtime environment")
    ENABLE_DOCS: bool = Field(default=True, description="Enable /docs and /redoc Swagger UI")

    # Paths
    BASE_DIR: Path = BACKEND_DIR
    UPLOAD_DIR: Path = BACKEND_DIR / "uploads"
    BACKUP_DIR: Path = BACKEND_DIR / "backups"
    STATIC_ADMIN_DIR: Path = BACKEND_DIR / "static_admin"

    # Database
    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{(BACKEND_DIR / 'database.sqlite').resolve().as_posix()}",
        description="SQLAlchemy async connection URL"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Ensure SQLite paths are resolved to absolute paths relative to BACKEND_DIR."""
        if isinstance(v, str) and ("sqlite+aiosqlite:///./" in v or "sqlite+aiosqlite://./" in v):
            clean_rel = v.replace("sqlite+aiosqlite:///.", "").replace("sqlite+aiosqlite://.", "").lstrip("/\\")
            abs_path = (BACKEND_DIR / clean_rel).resolve().as_posix()
            return f"sqlite+aiosqlite:///{abs_path}"
        return v
    SQLITE_BUSY_TIMEOUT_MS: int = Field(
        default=30000,
        description="Busy timeout in milliseconds to prevent database is locked errors"
    )

    # Security & JWT
    SECRET_KEY: SecretStr = Field(
        default=SecretStr("montazh-imperiya-super-secret-jwt-key-2026-production"),
        description="Secret key for signing JWT tokens"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://montazh.documentics.ru"
    ]

    # Media Upload Constraints
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB (supports HD loop video)
    ALLOWED_IMAGE_TYPES: Set[str] = {"image/jpeg", "image/png", "image/webp"}
    ALLOWED_VIDEO_TYPES: Set[str] = {"video/mp4", "video/webm"}

    # Default Admin Credentials
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin"

    def ensure_directories(self) -> None:
        """Creates necessary runtime directories if they do not exist."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        self.STATIC_ADMIN_DIR.mkdir(parents=True, exist_ok=True)


# Singleton settings instance
settings = Settings()
