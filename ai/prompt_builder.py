from __future__ import annotations

import json

_CONTEXT = (
    "Ты карьерный аналитик IT-рынка СНГ (Казахстан, Россия, Беларусь). "
    "Данные получены с hh.ru/hh.kz — реальные вакансии СНГ работодателей. "
    "Давай советы исходя из реалий СНГ рынка, не западного. "
)


class PromptBuilder:
    def combined_prompt(self, payload: dict[str, object]) -> str:
        return self._json_prompt(
            _CONTEXT +
            "Верни строгий JSON без markdown с двумя объектами: "
            "advisor={current_level, market_match, top_strengths, critical_gaps, recommendations, market_overview}; "
            "resume_gap={missing_skills, missing_technologies, knowledge_gaps, summary}.",
            payload,
        )

    def advisor_prompt(self, payload: dict[str, object]) -> str:
        return self._json_prompt(
            _CONTEXT +
            "Верни строгий JSON с полями: "
            "current_level, market_match, top_strengths, critical_gaps, recommendations, market_overview.",
            payload,
        )

    def resume_gap_prompt(self, payload: dict[str, object]) -> str:
        return self._json_prompt(
            _CONTEXT +
            "Сравни резюме с рынком СНГ. Верни строгий JSON с полями: "
            "missing_skills, missing_technologies, knowledge_gaps, summary.",
            payload,
        )

    def _json_prompt(self, instruction: str, payload: dict[str, object]) -> str:
        return f"{instruction}\n\nДанные рынка (агрегировано с hh.ru/hh.kz):\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
