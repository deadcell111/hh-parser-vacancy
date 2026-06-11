from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # python-dotenv не установлен — переменные берём из окружения напрямую

from app.bootstrap import run


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
