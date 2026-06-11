from __future__ import annotations

from dataclasses import dataclass, field

from parser.models import VacancyData


@dataclass
class MarketSummary:
    vacancies_found: int = 0
    resume_match: int = 0
    unique_skills: int = 0
    top_skills: list[dict[str, object]] = field(default_factory=list)
    top_duties: list[dict[str, object]] = field(default_factory=list)
    top_requirements: list[dict[str, object]] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)


@dataclass
class AnalysisState:
    vacancies: list[VacancyData] = field(default_factory=list)
    summary: MarketSummary = field(default_factory=MarketSummary)
    resume_result: dict[str, object] | None = None
    ai_advisor: dict[str, object] | None = None
    roadmap: dict[str, object] | None = None
