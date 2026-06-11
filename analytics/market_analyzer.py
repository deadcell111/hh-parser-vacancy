from __future__ import annotations

from analyzer.vacancy_analyzer import VacancyAnalyzer
from models.analysis import MarketSummary
from parser.models import VacancyData


class MarketAnalyzer:
    def __init__(self, vacancy_analyzer: VacancyAnalyzer | None = None) -> None:
        self.vacancy_analyzer = vacancy_analyzer or VacancyAnalyzer()

    def summarize(
        self,
        vacancies: list[VacancyData],
        resume_result: dict[str, object] | None = None,
    ) -> MarketSummary:
        stats = self.vacancy_analyzer.build_market_statistics(vacancies)
        skills = {skill["name"] for vacancy in vacancies for skill in vacancy.skills}
        return MarketSummary(
            vacancies_found=len(vacancies),
            resume_match=int((resume_result or {}).get("match_percent", 0)),
            unique_skills=len(skills),
            top_skills=stats["skills"].head(20).to_dict(orient="records") if not stats["skills"].empty else [],
            top_requirements=stats["requirements"].head(20).to_dict(orient="records") if not stats["requirements"].empty else [],
            missing_skills=list((resume_result or {}).get("missing_skills", []))[:30],
        )

    def to_ai_payload(self, summary: MarketSummary) -> dict[str, object]:
        return {
            "vacancies": summary.vacancies_found,
            "resume_match": summary.resume_match,
            "unique_skills": summary.unique_skills,
            "top_skills": summary.top_skills,
            "missing_skills": summary.missing_skills,
        }

