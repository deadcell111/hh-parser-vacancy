from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from analyzer.relevance import VacancyRelevanceScorer
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
        relevance: VacancyRelevanceScorer | None = None,
        market_analyzer: MarketAnalyzer | None = None,
    ) -> None:
        self.collector = collector
        self.parser = parser
        self.analyzer = analyzer or VacancyAnalyzer()
        self.relevance = relevance or VacancyRelevanceScorer()
        self.market_analyzer = market_analyzer or MarketAnalyzer(self.analyzer)

    def analyze_search(self, query: str, region: str, pages: int, workers: int, min_relevance: int) -> MarketRunResult:
        started = time.perf_counter()
        urls = self.collector.collect(query, region, pages)
        return self.analyze_urls(urls, workers, min_relevance, started)

    def analyze_urls(self, urls: list[str], workers: int, min_relevance: int, started: float | None = None) -> MarketRunResult:
        started = started or time.perf_counter()
        parsed = self.parser.parse_many(urls, workers=workers)
        admitted = []
        filtered = []
        for vacancy in parsed:
            vacancy = self.analyzer.analyze(vacancy)
            vacancy = self.relevance.apply(vacancy, min_relevance)
            if vacancy.is_relevant:
                admitted.append(vacancy)
            else:
                filtered.append(vacancy)
        summary = self.market_analyzer.summarize(admitted, filtered)
        elapsed = max(time.perf_counter() - started, 0.001)
        return MarketRunResult(
            state=AnalysisState(vacancies=admitted, filtered_vacancies=filtered, summary=summary),
            elapsed_seconds=elapsed,
            vacancies_per_minute=(len(parsed) / elapsed) * 60,
        )
