from __future__ import annotations

import os
import time
import threading
import logging
from typing import Any


try:
    import requests
except ImportError as exc:
    raise ImportError("requests не установлен: pip install requests") from exc


class HHApiError(RuntimeError):
    pass


class HHApiClient:
    """Единственная точка входа к HH API. Хранит токен, обновляет его, делает запросы с ретраями."""

    BASE_URL = "https://api.hh.ru"
    TOKEN_URL = "https://hh.ru/oauth/token"
    _REFRESH_BEFORE_SEC = 60

    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        if not client_id or not client_secret:
            raise ValueError("HH_CLIENT_ID и HH_CLIENT_SECRET обязательны")
        self.client_id = client_id
        self.client_secret = client_secret

        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.9",
        })

        self._token: str | None = None
        self._token_expires_at: float = 0.0
        self._lock = threading.Lock()
        self._areas_cache: list[dict] | None = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_env(cls) -> "HHApiClient":
        return cls(
            client_id=os.getenv("HH_CLIENT_ID", ""),
            client_secret=os.getenv("HH_CLIENT_SECRET", ""),
            user_agent=os.getenv("HH_USER_AGENT", "HHCareerIntelligence/1.0"),
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.BASE_URL}{path}"
        last_exc: Exception | None = None

        for attempt in range(4):
            if attempt:
                wait = min(2 ** attempt, 30)
                self.logger.debug("Retry %d/%d, waiting %ds", attempt, 3, wait)
                time.sleep(wait)

            token = self._ensure_token()
            headers = {"Authorization": f"Bearer {token}"}

            try:
                t0 = time.perf_counter()
                resp = self._session.request(method, url, headers=headers, timeout=30, **kwargs)
                elapsed = time.perf_counter() - t0
                self.logger.debug("%s %s → %d (%.2fs)", method, path, resp.status_code, elapsed)

                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 2 ** (attempt + 1)))
                    self.logger.warning("Rate limit (429), жду %ds", retry_after)
                    time.sleep(retry_after)
                    continue

                if resp.status_code == 503:
                    last_exc = HHApiError("HH API 503")
                    continue

                if resp.status_code == 403:
                    self.logger.warning("403 — пробую обновить токен")
                    with self._lock:
                        self._token = None
                    continue

                resp.raise_for_status()
                return resp.json()

            except requests.RequestException as exc:
                last_exc = exc

        raise HHApiError(f"HH API недоступен после {4} попыток: {last_exc}")

    def _ensure_token(self) -> str:
        with self._lock:
            if self._token and time.time() < self._token_expires_at - self._REFRESH_BEFORE_SEC:
                return self._token
            self._refresh_token_locked()
            return self._token  # type: ignore[return-value]

    def _refresh_token_locked(self) -> None:
        resp = self._session.post(
            self.TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise HHApiError(f"Не удалось получить токен: {exc}") from exc

        data = resp.json()
        self._token = data["access_token"]
        expires_in = data.get("expires_in", 7200)
        self._token_expires_at = time.time() + expires_in
        self.logger.info("Токен обновлён, истекает через %ds", expires_in)

    def areas(self) -> list[dict]:
        """Справочник регионов с кешем."""
        if self._areas_cache is not None:
            return self._areas_cache
        data = self.get("/areas")
        self._areas_cache = data if isinstance(data, list) else [data]
        return self._areas_cache

    def find_area_id(self, name: str) -> str | None:
        """Поиск ID региона по названию (регистр не важен)."""
        target = name.strip().lower()

        def _search(areas: list[dict]) -> str | None:
            for area in areas:
                if area.get("name", "").lower() == target:
                    return str(area["id"])
                found = _search(area.get("areas", []))
                if found:
                    return found
            return None

        return _search(self.areas())
