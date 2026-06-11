from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "HH Career Intelligence"
    database_path: Path = field(default_factory=lambda: _PROJECT_ROOT / "data" / "hh_career_intelligence.sqlite3")
    gemini_model: str = "gemini-2.5-flash"
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    hh_client_id: str = field(default_factory=lambda: os.getenv("HH_CLIENT_ID", ""))
    hh_client_secret: str = field(default_factory=lambda: os.getenv("HH_CLIENT_SECRET", ""))
    hh_user_agent: str = field(default_factory=lambda: os.getenv("HH_USER_AGENT", "HHCareerIntelligence/1.0"))
    default_region: str = "Алматы"
    default_pages: int = 1
    default_workers: int = 5
    min_relevance: int = 50


def load_config() -> AppConfig:
    local_settings = _PROJECT_ROOT / "data" / "settings.local.json"
    values: dict = {}
    if local_settings.exists():
        values = json.loads(local_settings.read_text(encoding="utf-8"))
    return AppConfig(
        gemini_api_key=values.get("gemini_api_key") or os.getenv("GEMINI_API_KEY", ""),
        gemini_model=values.get("gemini_model") or "gemini-2.5-flash",
        hh_client_id=values.get("hh_client_id") or os.getenv("HH_CLIENT_ID", ""),
        hh_client_secret=values.get("hh_client_secret") or os.getenv("HH_CLIENT_SECRET", ""),
        hh_user_agent=values.get("hh_user_agent") or os.getenv("HH_USER_AGENT", "HHCareerIntelligence/1.0"),
    )
