from __future__ import annotations

from pathlib import Path

from analyzer.skill_catalog import SKILL_CATALOG
from analyzer.vacancy_analyzer import VacancyAnalyzer
from parser.models import VacancyData


class ResumeChecker:
    def __init__(self) -> None:
        self.analyzer = VacancyAnalyzer()

    def load_text(self, path: str | Path) -> str:
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".docx":
            return self._read_docx(path)
        if suffix == ".pdf":
            return self._read_pdf(path)
        raise ValueError("Поддерживаются только DOCX, PDF и TXT")

    def compare(self, resume_path: str | Path, vacancies: list[VacancyData]) -> dict[str, object]:
        resume_text = self.load_text(resume_path)
        resume_skills = {skill["name"].lower() for skill in self.analyzer.extract_skills(resume_text)}
        vacancy_skills = {skill["name"] for vacancy in vacancies for skill in vacancy.skills}

        if not vacancy_skills:
            return {"match_percent": 0, "missing_skills": [], "matched_skills": []}

        matched = sorted(skill for skill in vacancy_skills if skill.lower() in resume_skills)
        missing = sorted(skill for skill in vacancy_skills if skill.lower() not in resume_skills)
        match_percent = round(len(matched) / len(vacancy_skills) * 100)
        market_stats = self.analyzer.build_skill_stats(vacancies)
        top_market = market_stats["Навык"].head(25).tolist() if not market_stats.empty else []
        recommendations = self._build_recommendations(missing, top_market)
        return {
            "match_percent": match_percent,
            "missing_skills": missing,
            "matched_skills": matched,
            "market_skills": top_market,
            "recommendations": recommendations,
        }

    def compare_text(self, resume_text: str, vacancies: list[VacancyData]) -> dict[str, object]:
        temp = Path(__file__).parent.parent / "data" / "_resume_temp.txt"
        temp.parent.mkdir(parents=True, exist_ok=True)
        temp.write_text(resume_text, encoding="utf-8")
        try:
            return self.compare(temp, vacancies)
        finally:
            if temp.exists():
                temp.unlink()

    def _read_docx(self, path: Path) -> str:
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError("Для чтения DOCX установите python-docx") from exc

        document = Document(path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    def _read_pdf(self, path: Path) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Для чтения PDF установите pypdf") from exc

        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _build_recommendations(self, missing: list[str], top_market: list[str]) -> list[str]:
        priority = [skill for skill in top_market if skill in missing]
        recommendations = [f"Добавить {skill}" for skill in priority[:20]]
        categories = self._missing_categories(priority)
        recommendations.extend(categories)
        return recommendations[:30]

    def _missing_categories(self, missing: list[str]) -> list[str]:
        category_hits = []
        missing_lower = {skill.lower() for skill in missing}
        for category, skills in SKILL_CATALOG.items():
            if any(skill.lower() in missing_lower for skill in skills):
                category_hits.append(f"Добавить опыт: {category}")
        return category_hits[:10]
