from __future__ import annotations

import asyncio
import hashlib
import json

from database.repositories import AICacheRepository


class GeminiService:
    def __init__(self, api_key: str, model: str, cache: AICacheRepository | None = None) -> None:
        self.api_key = api_key
        self.model = model
        self.cache = cache

    async def generate_json(self, prompt: str) -> dict[str, object]:
        cache_key = self.cache_key(prompt)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        if not self.api_key:
            response = self._offline_response()
        else:
            response = await asyncio.to_thread(self._generate_sync, prompt)
        if self.cache:
            self.cache.set(cache_key, self.model, response)
        return response

    def cache_key(self, prompt: str) -> str:
        return hashlib.sha256(f"{self.model}:v1:{prompt}".encode("utf-8")).hexdigest()

    def _generate_sync(self, prompt: str) -> dict[str, object]:
        from google import genai

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(model=self.model, contents=prompt)
        text = response.text or "{}"
        return self._parse_json(text)

    def _parse_json(self, text: str) -> dict[str, object]:
        text = text.strip()
        if text.startswith("```"):
            text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)

    def _offline_response(self) -> dict[str, object]:
        return {
            "advisor": {
                "current_level": "N/A",
                "market_match": 0,
                "top_strengths": ["Добавьте GEMINI_API_KEY в Settings или переменные окружения."],
                "critical_gaps": [],
                "salary_potential": "Недоступно без Gemini API",
                "recommendations": ["Настройте Gemini API key для AI-рекомендаций."],
                "market_overview": "AI Advisor работает в offline fallback режиме.",
            },
            "resume_gap": {
                "missing_skills": [],
                "missing_technologies": [],
                "knowledge_gaps": [],
                "salary_growth_skills": [],
                "summary": "Недоступно без Gemini API.",
            },
            "roadmap": {"weeks": []},
        }
