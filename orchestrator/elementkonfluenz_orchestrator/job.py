"""Dry-run job writer for the first Hermes orchestration contract."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from .result import JobResult


_SAFE_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """Create a simple filesystem-safe slug from a topic string."""
    lowered = value.strip().lower()
    slug = _SAFE_SLUG_RE.sub("-", lowered).strip("-")
    return slug or "untitled-topic"


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_job_id(topic: str) -> str:
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H%M%S")
    return f"{timestamp}_{slugify(topic)}"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create_dry_run_job(
    *,
    topic: str,
    out_dir: Path,
    job_id: str | None = None,
    locale: str = "de",
    period_days: int = 1825,
) -> JobResult:
    """Create the first Hermes-compatible dry-run job folder.

    This function intentionally does not call market data providers, renderers, SEO engines,
    distribution APIs, or other production systems. It only writes the contract artifacts.
    """
    resolved_job_id = job_id or out_dir.name or default_job_id(topic)
    generated_at = utc_now_iso()

    out_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = out_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    topic_brief = {
        "contract_version": "0.1",
        "topic_id": slugify(topic),
        "title": topic,
        "hook": topic,
        "assets": ["PLACEHOLDER_A", "PLACEHOLDER_B"],
        "period_days": period_days,
        "locale": locale,
        "content_angle": "comparison",
        "risk_level": "medium",
        "requires_review": True,
        "notes": [
            "Dry-run placeholder topic brief. Replace placeholder assets before production rendering.",
            "No market data was fetched in this orchestrator smoke test.",
        ],
    }

    sources = {
        "contract_version": "0.1",
        "job_id": resolved_job_id,
        "generated_at": generated_at,
        "sources": [
            {
                "source_id": "dry_run_manual_topic",
                "source_type": "manual_note",
                "name": "Manual dry-run topic input",
                "retrieved_at": generated_at,
                "limitations": [
                    "This is a contract smoke test, not a factual production run.",
                    "No external data source was queried.",
                ],
            }
        ],
    }

    log_text = "\n".join(
        [
            f"{generated_at} orchestrator dry-run started",
            f"job_id={resolved_job_id}",
            f"topic={topic}",
            "wrote topic_brief.json",
            "wrote sources.json",
            "wrote job_result.json",
            "no render, SEO, distribution, or publish step executed",
            "",
        ]
    )

    write_json(out_dir / "topic_brief.json", topic_brief)
    write_json(out_dir / "sources.json", sources)
    (logs_dir / "orchestrator.log").write_text(log_text, encoding="utf-8")

    result = JobResult(
        job_id=resolved_job_id,
        ok=True,
        artifacts=[
            "topic_brief.json",
            "sources.json",
            "job_result.json",
            "logs/orchestrator.log",
        ],
        warnings=[
            "Dry-run only: no market data fetched, no video rendered, no metadata generated, no posting attempted.",
            "Placeholder assets must be replaced by trend-engine output before production use.",
        ],
        message="Dry-run job folder created successfully.",
        requires_review=True,
        ready_to_publish=False,
    )
    result.write(out_dir / "job_result.json")
    return result
