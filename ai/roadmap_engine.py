from __future__ import annotations

from ai.gemini_service import GeminiService
from ai.prompt_builder import PromptBuilder


class LearningRoadmapEngine:
    def __init__(self, gemini: GeminiService, prompts: PromptBuilder | None = None) -> None:
        self.gemini = gemini
        self.prompts = prompts or PromptBuilder()

    async def build(self, payload: dict[str, object]) -> dict[str, object]:
        return await self.gemini.generate_json(self.prompts.roadmap_prompt(payload))
