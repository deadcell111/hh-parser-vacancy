from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from parser.hh_api_client import HHApiClient
from parser.models import VacancyData
from utils.logger import setup_logger


class HHParserError(ValueError):
    pass


class HHVacancyParser:
    """Загружает вакансии через HH API. Поддерживает одиночные и батч-запросы."""

    HH_HOST_RE = re.compile(r"(^|\.)hh\.(ru|kz)$", re.I)
    VACANCY_ID_RE = re.compile(r"/vacancy/(\d+)", re.I)

    def __init__(self, client: HHApiClient) -> None:
        self.client = client
        self.logger = setup_logger(self.__class__.__name__)

    def extract_vacancy_id(self, url: str) -> str:
        url = url.strip()
        if url.isdigit():
            return url
        parsed = urlparse(url)
        if parsed.scheme in {"http", "https"}:
            if not self.HH_HOST_RE.search(parsed.netloc):
                raise HHParserError(f"Не ссылка HH: {url}")
            match = self.VACANCY_ID_RE.search(parsed.path)
            if match:
                return match.group(1)
        raise HHParserError(f"Не удалось извлечь ID вакансии из: {url}")

    def parse(self, url: str) -> VacancyData:
        vacancy_id = self.extract_vacancy_id(url)
        return self._fetch(vacancy_id, url)

    def parse_many(self, urls: list[str], workers: int = 5) -> list[VacancyData]:
        unique = self._dedupe(urls)
        workers = max(1, min(int(workers or 5), 10))
        results: list[VacancyData] = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(self.parse, url): url for url in unique}
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as exc:
                    self.logger.warning("Пропущена вакансия %s: %s", futures[future], exc)
        return results

    def _fetch(self, vacancy_id: str, original_url: str) -> VacancyData:
        self.logger.info("Fetching vacancy %s", vacancy_id)
        data = self.client.get(f"/vacancies/{vacancy_id}")

        salary_raw = data.get("salary") or {}
        area = data.get("area") or {}
        employer = data.get("employer") or {}
        key_skills = [s["name"] for s in data.get("key_skills", []) if s.get("name")]

        description_html = data.get("description") or ""
        full_text = self._clean_html(description_html) if description_html else ""

        return VacancyData(
            url=data.get("alternate_url") or original_url,
            vacancy_id=vacancy_id,
            title=data.get("name", ""),
            company=employer.get("name", ""),
            city=area.get("name", ""),
            salary=self._format_salary(salary_raw),
            salary_from=salary_raw.get("from"),
            salary_to=salary_raw.get("to"),
            salary_currency=salary_raw.get("currency", ""),
            salary_gross=bool(salary_raw.get("gross", False)),
            employer_id=str(employer.get("id", "")),
            area_id=str(area.get("id", "")),
            full_text=full_text,
            key_skills=key_skills,
            skills=[{"name": s, "category": "Ключевые навыки"} for s in key_skills],
        )

    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def _format_salary(self, salary: dict) -> str:
        if not salary:
            return ""
        parts = []
        if salary.get("from"):
            parts.append(f"от {salary['from']:,}")
        if salary.get("to"):
            parts.append(f"до {salary['to']:,}")
        currency = salary.get("currency", "")
        gross = " (до вычета налогов)" if salary.get("gross") else ""
        return " ".join(parts) + (f" {currency}" if currency else "") + gross

    def _dedupe(self, urls: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for url in urls:
            try:
                vid = self.extract_vacancy_id(url)
            except HHParserError:
                result.append(url)
                continue
            if vid not in seen:
                seen.add(vid)
                result.append(url)
        return result
