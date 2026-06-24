from __future__ import annotations


class SourceItem:
    def __init__(self, source_id: str, item_id: str, title: str, attention: int, velocity: int, assets: list[str], keywords: list[str] | None = None, notes: str = "") -> None:
        self.source_id = source_id
        self.item_id = item_id
        self.title = title
        self.attention = attention
        self.velocity = velocity
        self.assets = assets
        self.keywords = keywords or []
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "item_id": self.item_id,
            "title": self.title,
            "attention": self.attention,
            "velocity": self.velocity,
            "assets": self.assets,
            "keywords": self.keywords,
            "notes": self.notes,
        }
