from __future__ import annotations

from typing import Protocol

from .item import SourceItem


class SourceAdapter(Protocol):
    source_id: str

    def collect(self) -> list[SourceItem]:
        ...
