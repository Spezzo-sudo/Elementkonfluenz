"""Job result helpers for Hermes-readable status files."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "0.1"


@dataclass
class JobResult:
    """Machine-readable result written after every orchestrator run."""

    job_id: str
    ok: bool
    stage: str = "orchestrator"
    requires_review: bool = True
    ready_to_publish: bool = False
    artifacts: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    message: str = ""
    retryable: bool | None = None
    error_code: str | None = None
    contract_version: str = CONTRACT_VERSION

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: value for key, value in data.items() if value is not None}

    def write(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
