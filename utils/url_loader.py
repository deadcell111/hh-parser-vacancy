from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


def load_urls(path: str | Path) -> list[str]:
    path = Path(path)
    if path.suffix.lower() == ".txt":
        return _clean_urls(path.read_text(encoding="utf-8").splitlines())
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            rows = csv.reader(file)
            values = [cell for row in rows for cell in row]
        return _clean_urls(values)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        frame = pd.read_excel(path, header=None)
        values = [str(value) for value in frame.to_numpy().flatten() if pd.notna(value)]
        return _clean_urls(values)
    raise ValueError("Поддерживаются только TXT, CSV и XLSX")


def _clean_urls(values: list[str]) -> list[str]:
    urls = []
    for value in values:
        value = value.strip()
        if value and not value.startswith("#"):
            urls.append(value)
    return urls
