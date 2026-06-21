"""SQLite-backed selection history: powers cooldown/dedup and anti-repetition checks."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "trend_history.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS selections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    tag TEXT,
    selected_at TEXT NOT NULL
);
"""


class HistoryStore:
    def __init__(self, db_path: Union[Path, str] = DEFAULT_DB_PATH):
        self.db_path = db_path if db_path == ":memory:" else Path(db_path)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def record(
        self,
        content_type: str,
        topic_id: str,
        tag: Optional[str],
        when: Optional[datetime] = None,
    ) -> None:
        when = when or datetime.now(timezone.utc)
        self._conn.execute(
            "INSERT INTO selections (content_type, topic_id, tag, selected_at) VALUES (?, ?, ?, ?)",
            (content_type, topic_id, tag, when.isoformat()),
        )
        self._conn.commit()

    def recent_content_types(self, limit: int) -> list[str]:
        rows = self._conn.execute(
            "SELECT content_type FROM selections ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [r[0] for r in rows]

    def topic_last_used(self, topic_id: str) -> Optional[datetime]:
        row = self._conn.execute(
            "SELECT selected_at FROM selections WHERE topic_id = ? ORDER BY id DESC LIMIT 1",
            (topic_id,),
        ).fetchone()
        return datetime.fromisoformat(row[0]) if row else None

    def content_type_counts(self) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT content_type, COUNT(*) FROM selections GROUP BY content_type"
        ).fetchall()
        return {content_type: count for content_type, count in rows}

    def tag_last_used(self, content_type: str, tag: str) -> Optional[datetime]:
        row = self._conn.execute(
            "SELECT selected_at FROM selections WHERE content_type = ? AND tag = ? ORDER BY id DESC LIMIT 1",
            (content_type, tag),
        ).fetchone()
        return datetime.fromisoformat(row[0]) if row else None

    def close(self) -> None:
        self._conn.close()
