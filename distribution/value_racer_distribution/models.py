"""GateDecision — the distribution gate's output contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class GateDecision:
    status: str  # "auto_post" | "pending_review"
    reasons: List[str] = field(default_factory=list)

    @property
    def auto_post(self) -> bool:
        return self.status == "auto_post"
