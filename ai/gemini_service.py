from __future__ import annotations

import asyncio
import hashlib
import json
import time

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

    _RETRY_DELAYS = (2, 5, 15, 30)

    def _generate_sync(self, prompt: str) -> dict[str, object]:
        from google import genai

        try:
            from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
            _retryable = (ResourceExhausted, ServiceUnavailable)
        except ImportError:
            _retryable = ()  # type: ignore[assignment]

        client = genai.Client(api_key=self.api_key)
        last_exc: Exception | None = None
        for delay in (*self._RETRY_DELAYS, None):
            try:
                response = client.models.generate_content(model=self.model, contents=prompt)
                return self._parse_json(response.text or "{}")
            except Exception as exc:
                is_retryable = (
                    (_retryable and isinstance(exc, _retryable))
                    or "503" in str(exc)
                    or "UNAVAILABLE" in str(exc)
                    or "429" in str(exc)
                    or "ResourceExhausted" in type(exc).__name__
                )
                if not is_retryable:
                    raise
                last_exc = exc
                if delay is None:
                    break
                time.sleep(delay)
        raise last_exc  # type: ignore[misc]

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
                "recommendations": ["Настройте Gemini API key для AI-рекомендаций."],
                "market_overview": "AI Advisor работает в offline fallback режиме.",
            },
            "resume_gap": {
                "missing_skills": [],
                "missing_technologies": [],
                "knowledge_gaps": [],
                "summary": "Недоступно без Gemini API.",
            },
        }
