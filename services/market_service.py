from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from analyzer.vacancy_analyzer import VacancyAnalyzer
from analytics.market_analyzer import MarketAnalyzer
from models.analysis import AnalysisState


@dataclass
class MarketRunResult:
    state: AnalysisState
    elapsed_seconds: float
    vacancies_per_minute: float


class MarketService:
    # collector: любой объект с методом collect(query, region, pages) -> list[str]
    # parser:    любой объект с методом parse_many(urls, workers) -> list[VacancyData]
    def __init__(
        self,
        collector: Any,
        parser: Any,
        analyzer: VacancyAnalyzer | None = None,
        market_analyzer: MarketAnalyzer | None = None,
    ) -> None:
        self.collector = collector
        self.parser = parser
        self.analyzer = analyzer or VacancyAnalyzer()
        self.market_analyzer = market_analyzer or MarketAnalyzer(self.analyzer)

    def analyze_search(self, query: str, region: str, pages: int, workers: int) -> MarketRunResult:
        started = time.perf_counter()
        urls = self.collector.collect(query, region, pages)
        vacancies = [self.analyzer.analyze(v) for v in self.parser.parse_many(urls, workers=workers)]
        summary = self.market_analyzer.summarize(vacancies)
        elapsed = max(time.perf_counter() - started, 0.001)
        return MarketRunResult(
            state=AnalysisState(vacancies=vacancies, summary=summary),
            elapsed_seconds=elapsed,
            vacancies_per_minute=(len(vacancies) / elapsed) * 60,
        )
