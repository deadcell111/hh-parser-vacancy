from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QMainWindow, QProgressBar, QStackedWidget, QVBoxLayout, QWidget

from ai.ai_advisor_engine import AIAdvisorEngine
from ai.roadmap_engine import LearningRoadmapEngine
from ai.resume_gap_engine import ResumeGapEngine
from analytics.market_analyzer import MarketAnalyzer
from app.config import AppConfig
from database.db import Database
from database.repositories import AICacheRepository, VacancyRepository
from export.saas_report_exporter import SaaSReportExporter
from models.analysis import AnalysisState
from resume_checker.resume_checker import ResumeChecker
from services.market_service import MarketService
from utils.url_loader import load_urls
from ui.analytics_pages import TopTablePage
from ui.exports_page import ExportsPage
from ui.market_page import MarketPage
from ui.navigation import NavigationSidebar
from ui.settings_page import SettingsPage
from ui.text_report_page import TextReportPage
from ui.resume_gap_page import ResumeGapPage
from ai.prompt_builder import PromptBuilder


class MarketWorker(QThread):
    completed = pyqtSignal(object, float, float)
    failed = pyqtSignal(str)

    def __init__(self, service: MarketService, query: str, region: str, pages: int, workers: int, min_relevance: int) -> None:
        super().__init__()
        self.service = service
        self.query = query
        self.region = region
        self.pages = pages
        self.workers = workers
        self.min_relevance = min_relevance

    def run(self) -> None:
        try:
            result = self.service.analyze_search(self.query, self.region, self.pages, self.workers, self.min_relevance)
            self.completed.emit(result.state, result.elapsed_seconds, result.vacancies_per_minute)
        except Exception as exc:
            self.failed.emit(str(exc))


class UrlAnalysisWorker(QThread):
    completed = pyqtSignal(object, float, float)
    failed = pyqtSignal(str)

    def __init__(self, service: MarketService, urls: list[str], workers: int, min_relevance: int) -> None:
        super().__init__()
        self.service = service
        self.urls = urls
        self.workers = workers
        self.min_relevance = min_relevance

    def run(self) -> None:
        try:
            result = self.service.analyze_urls(self.urls, self.workers, self.min_relevance)
            self.completed.emit(result.state, result.elapsed_seconds, result.vacancies_per_minute)
        except Exception as exc:
            self.failed.emit(str(exc))


class AIWorker(QThread):
    completed = pyqtSignal(object, object, object)
    failed = pyqtSignal(str)

    def __init__(self, advisor: AIAdvisorEngine, gap: ResumeGapEngine, roadmap: LearningRoadmapEngine, payload: dict[str, object]) -> None:
        super().__init__()
        self.advisor = advisor
        self.gap = gap
        self.roadmap = roadmap
        self.payload = payload

    def run(self) -> None:
        try:
            async def task():
                prompt = PromptBuilder().combined_prompt(self.payload)
                response = await self.advisor.gemini.generate_json(prompt)
                return (
                    response.get("advisor", {}),
                    response.get("resume_gap", {}),
                    response.get("roadmap", {}),
                )

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                advisor, gap, roadmap = loop.run_until_complete(task())
            finally:
                loop.close()
                asyncio.set_event_loop(None)
            self.completed.emit(advisor, gap, roadmap)
        except Exception as exc:
            self.failed.emit(str(exc))


class ExportWorker(QThread):
    completed = pyqtSignal(object, float, object)
    failed = pyqtSignal(str)

    def __init__(self, exporter: SaaSReportExporter, state: AnalysisState, directory: str) -> None:
        super().__init__()
        self.exporter = exporter
        self.state = state
        self.directory = directory

    def run(self) -> None:
        try:
            started = time.perf_counter()
            files = self.exporter.export(self.state, self.directory)
            elapsed = time.perf_counter() - started
            sizes = {
                "xlsx": next((Path(path).stat().st_size for path in files if str(path).lower().endswith(".xlsx")), 0),
                "pdf": next((Path(path).stat().st_size for path in files if str(path).lower().endswith(".pdf")), 0),
            }
            self.completed.emit(files, elapsed, sizes)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: AppConfig,
        market_service: MarketService,
        market_analyzer: MarketAnalyzer,
        vacancy_repository: VacancyRepository,
        advisor_engine: AIAdvisorEngine,
        gap_engine: ResumeGapEngine,
        roadmap_engine: LearningRoadmapEngine,
        exporter: SaaSReportExporter,
    ) -> None:
        super().__init__()
        self.config = config
        self.market_service = market_service
        self.market_analyzer = market_analyzer
        self.vacancy_repository = vacancy_repository
        self.advisor_engine = advisor_engine
        self.gap_engine = gap_engine
        self.roadmap_engine = roadmap_engine
        self.exporter = exporter
        self.resume_checker = ResumeChecker()
        self.state = AnalysisState()
        self.market_worker: MarketWorker | None = None
        self.url_worker: UrlAnalysisWorker | None = None
        self.ai_worker: AIWorker | None = None
        self.export_worker: ExportWorker | None = None
        self.current_page_id = "market"
        self.dirty_pages: set[str] = set()
        self.loaded_pages: set[str] = set()

        self.setWindowTitle(config.app_name)
        self.resize(1440, 920)
        self._build()

    def _build(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar = NavigationSidebar()
        self.stack = QStackedWidget()
        self.pages: dict[str, QWidget] = {
            "market": MarketPage(),
            "advisor": TextReportPage("AI Advisor", "ai_advisor"),
            "resume": ResumeGapPage(),
            "roadmap": TextReportPage("Learning Roadmap", "roadmap"),
            "exports": ExportsPage(),
            "settings": SettingsPage(self.config.gemini_api_key, self.config.gemini_model),
        }
        self.pages["top_skills"] = TopTablePage("Ключевые навыки", "top_skills")
        self.pages["top_requirements"] = TopTablePage("ТОП требований", "top_requirements")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(22, 18, 22, 18)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        content_layout.addWidget(self.progress)
        content_layout.addWidget(self.stack)

        for page_id in ["market", "top_skills", "top_requirements", "advisor", "resume", "roadmap", "exports", "settings"]:
            self.stack.addWidget(self.pages[page_id])

        layout.addWidget(self.sidebar)
        layout.addWidget(content, stretch=1)
        self.setCentralWidget(root)

        self.sidebar.page_changed.connect(self._navigate)
        self.pages["market"].run_requested.connect(self._run_market)  # type: ignore[attr-defined]
        self.pages["market"].import_requested.connect(self._import_urls)  # type: ignore[attr-defined]
        self.pages["resume"].resume_upload_requested.connect(self._upload_resume)  # type: ignore[attr-defined]
        self.pages["exports"].export_requested.connect(self._export)  # type: ignore[attr-defined]
        self.pages["settings"].settings_saved.connect(self._save_settings)  # type: ignore[attr-defined]

    def _navigate(self, page_id: str) -> None:
        mapping = {
            "market": "market",
            "top_skills": "top_skills",
            "top_requirements": "top_requirements",
            "advisor": "advisor",
            "resume": "resume",
            "roadmap": "roadmap",
            "exports": "exports",
            "settings": "settings",
        }
        target = mapping.get(page_id, "market")
        self.current_page_id = target
        self.stack.setCurrentWidget(self.pages[target])
        self._refresh_page(target)

    def _run_market(self, query: str, region: str, pages: int, workers: int, min_relevance: int) -> None:
        self.progress.show()
        self.pages["market"].set_status("Running market analysis...")  # type: ignore[attr-defined]
        self.market_worker = MarketWorker(self.market_service, query, region, pages, workers, min_relevance)
        self.market_worker.completed.connect(self._market_completed)
        self.market_worker.failed.connect(self._task_failed)
        self.market_worker.start()

    def _import_urls(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import URLs", "", "URL files (*.txt *.csv *.xlsx *.xls);;All files (*.*)")
        if not path:
            return
        try:
            urls = load_urls(path)
        except Exception as exc:
            self._task_failed(str(exc))
            return
        self._run_urls(urls)

    def _run_urls(self, urls: list[str]) -> None:
        self.progress.show()
        self.pages["market"].set_status("Analyzing imported vacancies...")  # type: ignore[attr-defined]
        self.url_worker = UrlAnalysisWorker(self.market_service, urls, self.config.default_workers, self.config.min_relevance)
        self.url_worker.completed.connect(self._market_completed)
        self.url_worker.failed.connect(self._task_failed)
        self.url_worker.start()

    def _market_completed(self, state: AnalysisState, elapsed: float, speed: float) -> None:
        self.state = state
        self.vacancy_repository.upsert_many(state.vacancies)
        self._mark_dirty()
        self._refresh_page(self.current_page_id)
        self.pages["market"].set_status(f"Done in {elapsed:.1f}s, {speed:.1f} vacancies/min. Generating AI...")  # type: ignore[attr-defined]
        payload = self.market_analyzer.to_ai_payload(state.summary)
        self.ai_worker = AIWorker(self.advisor_engine, self.gap_engine, self.roadmap_engine, payload)
        self.ai_worker.completed.connect(self._ai_completed)
        self.ai_worker.failed.connect(self._task_failed)
        self.ai_worker.start()

    def _ai_completed(self, advisor: dict, gap: dict, roadmap: dict) -> None:
        self.state.ai_advisor = advisor
        self.state.resume_result = gap
        self.state.roadmap = roadmap
        self.progress.hide()
        self.pages["market"].set_status("Market analysis and AI reports completed.")  # type: ignore[attr-defined]
        self._mark_dirty()
        self._refresh_page(self.current_page_id)

    def _upload_resume(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Upload Resume", "", "Resume files (*.docx *.pdf *.txt);;All files (*.*)")
        if not path or not self.state.vacancies:
            return
        try:
            self.state.resume_result = self.resume_checker.compare(path, self.state.vacancies)
            self.state.summary = self.market_analyzer.summarize(self.state.vacancies, self.state.filtered_vacancies, self.state.resume_result)
            self._mark_dirty()
            self._refresh_page(self.current_page_id)
            payload = self.market_analyzer.to_ai_payload(self.state.summary)
            self.ai_worker = AIWorker(self.advisor_engine, self.gap_engine, self.roadmap_engine, payload)
            self.ai_worker.completed.connect(self._ai_completed)
            self.ai_worker.failed.connect(self._task_failed)
            self.ai_worker.start()
        except Exception as exc:
            self._task_failed(str(exc))

    def _task_failed(self, message: str) -> None:
        self.progress.hide()
        self.pages["market"].set_status(f"Error: {message}")  # type: ignore[attr-defined]

    def _mark_dirty(self) -> None:
        self.dirty_pages = set(self.pages.keys())

    def _refresh_page(self, page_id: str) -> None:
        if page_id not in self.dirty_pages and page_id in self.loaded_pages:
            return
        page = self.pages.get(page_id)
        update = getattr(page, "update_state", None)
        if update:
            update(self.state)
        self.loaded_pages.add(page_id)
        self.dirty_pages.discard(page_id)

    def _export(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Export report")
        if not directory:
            return
        self.progress.show()
        self.pages["exports"].set_status("Generating reports in background...")  # type: ignore[attr-defined]
        self.export_worker = ExportWorker(self.exporter, self.state, directory)
        self.export_worker.completed.connect(self._export_completed)
        self.export_worker.failed.connect(self._task_failed)
        self.export_worker.start()

    def _export_completed(self, files: list[Path], elapsed: float, sizes: dict[str, int]) -> None:
        self.progress.hide()
        self.pages["exports"].set_status("Exported: " + ", ".join(Path(path).name for path in files))  # type: ignore[attr-defined]
        self.pages["exports"].set_export_stats(elapsed, sizes)  # type: ignore[attr-defined]

    def _save_settings(self, api_key: str, model: str) -> None:
        path = self.config.database_path.parent / "settings.local.json"
        path.write_text(json.dumps({"gemini_api_key": api_key, "gemini_model": model}, ensure_ascii=False, indent=2), encoding="utf-8")
        self.advisor_engine.gemini.api_key = api_key
        self.gap_engine.gemini.api_key = api_key
        self.roadmap_engine.gemini.api_key = api_key
        self.advisor_engine.gemini.model = model
        self.gap_engine.gemini.model = model
        self.roadmap_engine.gemini.model = model
        self.pages["settings"].set_status("Settings saved locally. API key is not committed.")  # type: ignore[attr-defined]
