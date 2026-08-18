"""Production configuration with env validation."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "T4H Atlas ENH"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    api_prefix: str = "/api/v1"
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8080, alias="PORT")

    # Database — sqlite for local; set DATABASE_URL for Postgres
    database_url: str = Field(
        default=f"sqlite:///{ROOT / 'data' / 'atlas.db'}",
        alias="DATABASE_URL",
    )

    # Portal adapter secrets (optional until live scrape)
    grantconnect_api_key: Optional[str] = Field(default=None, alias="GRANTCONNECT_API_KEY")
    ukri_api_key: Optional[str] = Field(default=None, alias="UKRI_API_KEY")
    horizon_portal_token: Optional[str] = Field(default=None, alias="HORIZON_PORTAL_TOKEN")

    # Refresh cadence (cron-like hints for job runner)
    refresh_open_calls_hours: int = Field(default=168, alias="REFRESH_OPEN_CALLS_HOURS")  # weekly
    refresh_pattern_funders_hours: int = Field(default=720, alias="REFRESH_PATTERN_FUNDERS_HOURS")

    # Paths to seed data from grant-discovery package
    taxonomy_index_path: str = Field(
        default=str(ROOT / "data" / "taxonomy_grant_index.json"),
        alias="TAXONOMY_INDEX_PATH",
    )
    opportunities_seed_path: str = Field(
        default=str(ROOT / "data" / "opportunities.json"),
        alias="OPPORTUNITIES_SEED_PATH",
    )

    # Security
    api_key: Optional[str] = Field(default=None, alias="ATLAS_API_KEY")
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")

    @field_validator("app_env")
    @classmethod
    def env_ok(cls, v: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        if v not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_production_env() -> list[str]:
    """Return list of blocking issues for production boot."""
    s = get_settings()
    issues: list[str] = []
    if s.is_production:
        if s.database_url.startswith("sqlite"):
            issues.append("DATABASE_URL must not be sqlite in production")
        if not s.api_key:
            issues.append("ATLAS_API_KEY required in production")
        if s.debug:
            issues.append("DEBUG must be false in production")
    return issues
