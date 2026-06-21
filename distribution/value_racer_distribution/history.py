"""SQLite-backed post history: powers the imperium gate's first-contact check.

Separate from trend-engine's selection history (value_racer_trend/store.py), which records when a
topic was *picked for production*, not when an episode was actually *posted*. A topic can be
picked and rendered many times before its first post ever clears manual review.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "distribution_history.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    video_id TEXT NOT NULL,
    posted_at TEXT NOT NULL
);
"""


class PostHistory:
    def __init__(self, db_path: Union[Path, str] = DEFAULT_DB_PATH):
        self.db_path = db_path if db_path == ":memory:" else Path(db_path)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def record_post(
        self,
        content_type: str,
        topic_id: str,
        video_id: str,
        when: Optional[datetime] = None,
    ) -> None:
        when = when or datetime.now(timezone.utc)
        self._conn.execute(
            "INSERT INTO posts (content_type, topic_id, video_id, posted_at) VALUES (?, ?, ?, ?)",
            (content_type, topic_id, video_id, when.isoformat()),
        )
        self._conn.commit()

    def has_posted(self, topic_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM posts WHERE topic_id = ? LIMIT 1", (topic_id,)
        ).fetchone()
        return row is not None

    def close(self) -> None:
        self._conn.close()
