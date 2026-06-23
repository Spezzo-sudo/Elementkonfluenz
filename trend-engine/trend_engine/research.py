"""Dry-run trend scan core."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .catalog import CONTRACT_VERSION, read_history, utc_now_iso


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def perform_research(*, job_id: str, out_dir: Path, history_path: Path, topic_days: int = 14, pair_days: int = 21, write_history: bool = True) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    generated_at = utc_now_iso()
    _ = read_history(history_path)
    selected = {
        "topic_slug": "ai-vs-energy",
        "title": "AI vs Energy Demand",
        "video_type": "trend_explainer",
        "template": "chart_explainer",
        "assets": ["ai", "energy"],
        "asset_labels": ["AI", "Energy"],
        "keywords": ["ai", "energy", "technology"],
        "content_angle": "trend_explainer",
        "risk_level": "medium",
        "default_period_days": 1095,
        "source_signal_id": "simulated-ai-energy",
        "final_score": 91,
        "requires_review": True,
        "ready_to_publish": False,
    }
    scored = [selected]
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "trend_report.json", {"contract_version": CONTRACT_VERSION, "job_id": job_id, "run_mode": "trend_scan", "generated_at": generated_at, "mode": "dry_run", "research_window": "prepublish_t_minus_2h", "candidate_count": 1, "requires_review": True, "ready_to_publish": False})
    write_json(out_dir / "scored_candidates.json", scored)
    write_json(out_dir / "topic_brief.json", {"contract_version": CONTRACT_VERSION, "job_id": job_id, "run_mode": "trend_scan", "topic_id": selected["topic_slug"], "title": selected["title"], "hook": selected["title"], "video_type": selected["video_type"], "template": selected["template"], "assets": selected["assets"], "asset_labels": selected["asset_labels"], "keywords": selected["keywords"], "period_days": selected["default_period_days"], "locale": "de", "content_angle": selected["content_angle"], "risk_level": selected["risk_level"], "generated_at": generated_at, "trend_signal_id": selected["source_signal_id"], "trend_score": selected["final_score"], "requires_review": True, "ready_to_publish": False})
    write_json(out_dir / "sources.json", {"contract_version": CONTRACT_VERSION, "job_id": job_id, "generated_at": generated_at, "sources": [{"source_id": "simulated_trend_scan", "source_type": "local_dry_run", "name": "Simulated trend scan", "retrieved_at": generated_at}]})
    return selected, scored
