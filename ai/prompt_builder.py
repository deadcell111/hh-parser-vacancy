from __future__ import annotations

import json


class PromptBuilder:
    def combined_prompt(self, payload: dict[str, object]) -> str:
        return self._json_prompt(
            "Ты карьерный аналитик для IT-рынка. Верни строгий JSON без markdown с тремя объектами: "
            "advisor={current_level, market_match, top_strengths, critical_gaps, salary_potential, recommendations, market_overview}; "
            "resume_gap={missing_skills, missing_technologies, knowledge_gaps, salary_growth_skills, summary}; "
            "roadmap={weeks:[{week, skills, why, market_frequency, career_impact, practice_task}]}.",
            payload,
        )

    def advisor_prompt(self, payload: dict[str, object]) -> str:
        return self._json_prompt(
            "Ты карьерный аналитик для IT-рынка. Верни строгий JSON с полями: "
            "current_level, market_match, top_strengths, critical_gaps, salary_potential, recommendations, market_overview.",
            payload,
        )

    def resume_gap_prompt(self, payload: dict[str, object]) -> str:
        return self._json_prompt(
            "Сравни резюме с рынком. Верни строгий JSON с полями: missing_skills, missing_technologies, knowledge_gaps, salary_growth_skills, summary.",
            payload,
        )

    def roadmap_prompt(self, payload: dict[str, object]) -> str:
        return self._json_prompt(
            "Построй 6-недельный learning roadmap. Верни строгий JSON: weeks=[{week, skills, why, market_frequency, career_impact, practice_task}].",
            payload,
        )

    def _json_prompt(self, instruction: str, payload: dict[str, object]) -> str:
        return f"{instruction}\n\nДанные рынка, агрегировано, без сырых вакансий:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
