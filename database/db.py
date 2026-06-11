from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        schema = Path(__file__).parent / "schema.sql"
        connection = self.connect()
        try:
            connection.executescript(schema.read_text(encoding="utf-8"))
        finally:
            connection.close()
