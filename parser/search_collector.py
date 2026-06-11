from __future__ import annotations

from parser.hh_api_client import HHApiClient
from utils.logger import setup_logger


class HHSearchCollector:
    """Собирает ссылки на вакансии через HH API /vacancies."""

    def __init__(self, client: HHApiClient) -> None:
        self.client = client
        self.logger = setup_logger(self.__class__.__name__)

    def collect(
        self,
        query: str,
        region: str = "",
        pages: int = 1,
        per_page: int = 100,
    ) -> list[str]:
        query = query.strip()
        if not query:
            raise ValueError("Введите поисковый запрос")

        pages = max(1, min(int(pages or 1), 100))
        per_page = max(1, min(int(per_page or 100), 100))
        area_id = self._resolve_area(region) if region.strip() else None

        links: list[str] = []
        seen_ids: set[str] = set()

        for page_index in range(pages):
            params: dict = {"text": query, "page": page_index, "per_page": per_page}
            if area_id:
                params["area"] = area_id

            self.logger.info("Страница %d, запрос: %s", page_index + 1, query)
            data = self.client.get("/vacancies", params=params)

            items = data.get("items", [])
            if not items:
                self.logger.info("Пустая страница %d — остановка", page_index + 1)
                break

            for item in items:
                vid = str(item.get("id", ""))
                url = item.get("alternate_url", "")
                if vid and url and vid not in seen_ids:
                    seen_ids.add(vid)
                    links.append(url)

            total_pages = data.get("pages", 1)
            if page_index + 1 >= total_pages:
                self.logger.info("Достигнута последняя страница API (%d)", total_pages)
                break

        self.logger.info("Собрано уникальных вакансий: %d", len(links))
        return links

    def _resolve_area(self, region: str) -> str | None:
        value = region.strip()
        if not value:
            return None
        if value.isdigit():
            return value
        area_id = self.client.find_area_id(value)
        if area_id:
            return area_id
        self.logger.warning("Регион '%s' не найден в /areas, ищем без фильтра", region)
        return None
