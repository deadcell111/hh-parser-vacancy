CREATE TABLE IF NOT EXISTS vacancies (
    id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    city TEXT,
    salary TEXT,
    url TEXT,
    relevance_score INTEGER,
    full_text TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_cache (
    cache_key TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    response_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
