from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from ai.gemini_service import GeminiService
from analytics.market_analyzer import MarketAnalyzer
from app.config import load_config
from app.theme import APP_STYLESHEET
from database.db import Database
from database.repositories import AICacheRepository, VacancyRepository
from export.saas_report_exporter import SaaSReportExporter
from services.market_service import MarketService
from ui.main_window import MainWindow
from utils.logger import setup_logger


def _build_market_service(config, market_analyzer: MarketAnalyzer) -> MarketService:
    logger = setup_logger("bootstrap")

    if config.hh_client_id and config.hh_client_secret:
        from parser.hh_api_client import HHApiClient
        from parser.hh_parser import HHVacancyParser
        from parser.search_collector import HHSearchCollector
        client = HHApiClient(
            client_id=config.hh_client_id,
            client_secret=config.hh_client_secret,
            user_agent=config.hh_user_agent,
        )
        logger.info("Режим: HH API (client_id=%s...)", config.hh_client_id[:6])
        return MarketService(
            collector=HHSearchCollector(client),
            parser=HHVacancyParser(client),
            market_analyzer=market_analyzer,
        )

    try:
        from parser.hh_browser_fallback import HHBatchVacancyParser
        from parser.hh_browser_fallback import HHSearchCollector as BrowserCollector
        logger.warning("HH API ключи не заданы — используется браузерный парсер (Playwright)")
        return MarketService(
            collector=BrowserCollector(),
            parser=HHBatchVacancyParser(),
            market_analyzer=market_analyzer,
        )
    except ImportError:
        logger.error("Playwright не установлен и HH API ключи не заданы. Настройте .env")
        raise RuntimeError(
            "Нет источника данных.\n\n"
            "Добавьте HH_CLIENT_ID и HH_CLIENT_SECRET в файл .env\n"
            "или установите Playwright: pip install playwright && playwright install chromium"
        )


def run() -> int:
    config = load_config()
    database = Database(config.database_path)
    database.initialize()
    ai_cache = AICacheRepository(database)
    vacancy_repository = VacancyRepository(database)
    gemini = GeminiService(config.gemini_api_key, config.gemini_model, ai_cache)
    market_analyzer = MarketAnalyzer()
    market_service = _build_market_service(config, market_analyzer)
    exporter = SaaSReportExporter()

    app = QApplication(sys.argv)
    if sys.platform == "darwin":
        app.setStyle("Fusion")
        app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, True)
    app.setQuitOnLastWindowClosed(True)
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindow(config, market_service, market_analyzer, vacancy_repository, gemini, exporter)
    window.show()
    return app.exec()
