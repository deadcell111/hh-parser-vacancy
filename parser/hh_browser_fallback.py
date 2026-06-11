from __future__ import annotations

import re
import asyncio
from contextlib import suppress
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as AsyncPlaywrightTimeoutError
from playwright.async_api import async_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from parser.models import VacancyData
from utils.logger import setup_logger


class HHParserError(RuntimeError):
    pass


class HHVacancyParser:
    """Loads public HH vacancy pages with Playwright and extracts visible content."""

    VACANCY_ID_RE = re.compile(r"/vacancy/(\d+)(?:[/?#].*)?$", re.I)
    HH_HOST_RE = re.compile(r"(^|\.)hh\.(ru|kz)$", re.I)

    def __init__(self, timeout_ms: int = 20000, headless: bool = True) -> None:
        self.timeout_ms = timeout_ms
        self.headless = headless
        self.logger = setup_logger(self.__class__.__name__)

    def extract_vacancy_id(self, url: str) -> str:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or not self.HH_HOST_RE.search(parsed.netloc):
            raise HHParserError(f"Некорректная ссылка HH: {url}")
        match = self.VACANCY_ID_RE.search(parsed.path)
        if not match:
            raise HHParserError(f"Не найден ID вакансии в ссылке: {url}")
        return match.group(1)

    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url.strip())
        vacancy_id = self.extract_vacancy_id(url)
        return f"https://{parsed.netloc}/vacancy/{vacancy_id}"

    def parse(self, url: str) -> VacancyData:
        raw_url = url.strip()
        vacancy_id = self.extract_vacancy_id(raw_url)

        self.logger.info("Parsing vacancy: %s", raw_url)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                locale="ru-RU",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
            )
            page = context.new_page()
            try:
                page.goto(raw_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                with suppress(PlaywrightTimeoutError):
                    page.wait_for_load_state("load", timeout=6000)
                self._dismiss_popups(page)
                html = page.content()
                final_url = page.url
            except Exception as exc:
                raise HHParserError(f"Не удалось открыть вакансию: {exc}") from exc
            finally:
                context.close()
                browser.close()

        return self._extract_from_html(final_url or raw_url, vacancy_id, html)

    def _dismiss_popups(self, page) -> None:
        popup_buttons = [
            "button:has-text('Понятно')",
            "button:has-text('Принять')",
            "button:has-text('Закрыть')",
            "[data-qa='cookies-policy-informer-accept']",
        ]
        for selector in popup_buttons:
            with suppress(Exception):
                page.locator(selector).first.click(timeout=1500)

    def _extract_from_html(self, url: str, vacancy_id: str, html: str) -> VacancyData:
        soup = BeautifulSoup(html, "html.parser")

        title = self._first_text(soup, ["[data-qa='vacancy-title']", "h1[data-qa='bloko-header-1']", "h1"])
        company = self._first_text(
            soup,
            ["[data-qa='vacancy-company-name']", "[data-qa='vacancy-company-name'] span", ".vacancy-company-name"],
        )
        city = self._first_text(
            soup,
            [
                "[data-qa='vacancy-view-location']",
                "[data-qa='vacancy-view-raw-address']",
                "[data-qa='vacancy-serp__vacancy-address']",
            ],
        )
        salary = self._first_text(soup, ["[data-qa='vacancy-salary']", ".vacancy-title .bloko-header-section-2"])

        description = soup.select_one("[data-qa='vacancy-description']")
        full_text = description.get_text("\n", strip=True) if description else soup.get_text("\n", strip=True)
        full_text = self._clean_multiline(full_text)

        key_skills = [
            self._clean_text(tag.get_text(" ", strip=True))
            for tag in soup.select("[data-qa='bloko-tag__text'], [data-qa='skills-element']")
        ]
        key_skills = [skill for skill in dict.fromkeys(key_skills) if skill]

        return VacancyData(
            url=url,
            vacancy_id=vacancy_id,
            title=self._clean_text(title),
            company=self._clean_text(company),
            city=self._clean_text(city),
            salary=self._clean_text(salary),
            full_text=full_text,
            key_skills=key_skills,
            skills=[{"name": skill, "category": "Ключевые навыки"} for skill in key_skills],
        )

    def _first_text(self, soup: BeautifulSoup, selectors: list[str]) -> str:
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                text = node.get_text(" ", strip=True)
                if text:
                    return text
        return ""

    def _clean_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value or "").strip()

    def _clean_multiline(self, value: str) -> str:
        lines = [self._clean_text(line) for line in re.split(r"[\n\r]+", value or "")]
        return "\n".join(line for line in lines if line)


class HHBatchVacancyParser(HHVacancyParser):
    """Fetches many vacancy pages with one Chromium and one BrowserContext."""

    def parse_many(self, urls: list[str], workers: int = 5) -> list[VacancyData]:
        workers = max(1, min(int(workers or 5), 10))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._parse_many_async(urls, workers))
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    async def _parse_many_async(self, urls: list[str], workers: int) -> list[VacancyData]:
        unique_urls = self._dedupe_by_vacancy_id(urls)
        semaphore = asyncio.Semaphore(workers)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                locale="ru-RU",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
            )
            try:
                tasks = [self._parse_one_async(context, url, semaphore) for url in unique_urls]
                results = await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                await context.close()
                await browser.close()

        vacancies: list[VacancyData] = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.warning("Batch parser skipped vacancy: %s", result)
                continue
            vacancies.append(result)
        return vacancies

    async def _parse_one_async(self, context, url: str, semaphore: asyncio.Semaphore) -> VacancyData:
        async with semaphore:
            raw_url = url.strip()
            vacancy_id = self.extract_vacancy_id(raw_url)
            page = await context.new_page()
            try:
                await page.goto(raw_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                with suppress(AsyncPlaywrightTimeoutError):
                    await page.wait_for_load_state("load", timeout=5000)
                await self._dismiss_popups_async(page)
                html = await page.content()
                final_url = page.url
            except Exception as exc:
                raise HHParserError(f"Не удалось открыть вакансию {raw_url}: {exc}") from exc
            finally:
                await page.close()
            return self._extract_from_html(final_url or raw_url, vacancy_id, html)

    async def _dismiss_popups_async(self, page) -> None:
        popup_buttons = [
            "button:has-text('Понятно')",
            "button:has-text('Принять')",
            "button:has-text('Закрыть')",
            "[data-qa='cookies-policy-informer-accept']",
        ]
        for selector in popup_buttons:
            with suppress(Exception):
                await page.locator(selector).first.click(timeout=800)

    def _dedupe_by_vacancy_id(self, urls: list[str]) -> list[str]:
        result = []
        seen = set()
        for url in urls:
            try:
                vacancy_id = self.extract_vacancy_id(url)
            except HHParserError:
                result.append(url)
                continue
            if vacancy_id not in seen:
                seen.add(vacancy_id)
                result.append(url)
        return result


class HHSearchCollector:
    """Браузерный коллектор поиска (фолбэк без API ключей)."""

    REGION_MAP = {
        "алматы": ("hh.kz", "160"),
        "астана": ("hh.kz", "159"),
        "казахстан": ("hh.kz", "40"),
        "москва": ("hh.ru", "1"),
        "санкт-петербург": ("hh.ru", "2"),
        "спб": ("hh.ru", "2"),
        "россия": ("hh.ru", "113"),
    }

    def __init__(self, timeout_ms: int = 45000, headless: bool = True) -> None:
        self.timeout_ms = timeout_ms
        self.headless = headless
        self.logger = setup_logger(self.__class__.__name__)
        self._url_parser = HHVacancyParser()

    def collect(self, query: str, region: str = "", pages: int = 1) -> list[str]:
        from urllib.parse import urlencode, urljoin
        from bs4 import BeautifulSoup

        query = query.strip()
        if not query:
            raise ValueError("Введите поисковый запрос")
        pages = max(1, min(int(pages or 1), 100))
        host, area = self._resolve_region(region)

        links: list[str] = []
        seen_ids: set[str] = set()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(locale="ru-RU")
            page = context.new_page()
            try:
                for page_index in range(pages):
                    params: dict = {"text": query, "page": page_index}
                    if area:
                        params["area"] = area
                    url = f"https://{host}/search/vacancy?{urlencode(params)}"
                    self.logger.info("Collecting page: %s", url)
                    page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                    with suppress(PlaywrightTimeoutError):
                        page.wait_for_load_state("networkidle", timeout=10000)
                    html = page.content()
                    for link in self._extract_links(html, f"https://{host}", BeautifulSoup):
                        try:
                            vid = self._url_parser.extract_vacancy_id(link)
                        except HHParserError:
                            continue
                        if vid not in seen_ids:
                            seen_ids.add(vid)
                            links.append(link)
            finally:
                context.close()
                browser.close()
        return links

    def _resolve_region(self, region: str) -> tuple[str, str]:
        value = region.strip().lower()
        if not value:
            return "hh.kz", ""
        if value.isdigit():
            return "hh.kz", value
        return self.REGION_MAP.get(value, ("hh.kz", ""))

    def _extract_links(self, html: str, base_url: str, BeautifulSoup) -> list[str]:
        from urllib.parse import urljoin
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for sel in ["a[data-qa='serp-item__title']", "a[data-qa='vacancy-serp__vacancy-title']", "a[href*='/vacancy/']"]:
            for tag in soup.select(sel):
                href = tag.get("href")
                if href:
                    links.append(urljoin(base_url, href.split("?")[0]))
        return list(dict.fromkeys(links))
