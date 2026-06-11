from __future__ import annotations

import json

from database.db import Database
from parser.models import VacancyData


class VacancyRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def upsert_many(self, vacancies: list[VacancyData]) -> None:
        conn = self.database.connect()
        try:
            conn.executemany(
                """
                INSERT INTO vacancies(id, title, company, city, salary, url, full_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    company=excluded.company,
                    city=excluded.city,
                    salary=excluded.salary,
                    url=excluded.url,
                    full_text=excluded.full_text
                """,
                [
                    (
                        vacancy.vacancy_id,
                        vacancy.title,
                        vacancy.company,
                        vacancy.city,
                        vacancy.salary,
                        vacancy.url,
                        vacancy.full_text,
                    )
                    for vacancy in vacancies
                    if vacancy.vacancy_id
                ],
            )
            conn.commit()
        finally:
            conn.close()


class AICacheRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get(self, cache_key: str) -> dict | None:
        conn = self.database.connect()
        try:
            row = conn.execute(
                "SELECT response_json FROM ai_cache WHERE cache_key = ?", (cache_key,)
            ).fetchone()
            return json.loads(row["response_json"]) if row else None
        finally:
            conn.close()

    def set(self, cache_key: str, model: str, response: dict) -> None:
        conn = self.database.connect()
        try:
            conn.execute(
                """
                INSERT INTO ai_cache(cache_key, model, response_json)
                VALUES (?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET response_json=excluded.response_json
                """,
                (cache_key, model, json.dumps(response, ensure_ascii=False)),
            )
            conn.commit()
        finally:
            conn.close()
