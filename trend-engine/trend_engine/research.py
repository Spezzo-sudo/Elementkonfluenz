"""Dry-run trend scan core."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .catalog import CONTRACT_VERSION, normalize_slug, parse_timestamp, read_history, utc_now_iso


CANDIDATES: list[dict[str, Any]] = [
    {
        "signal_id": "ai-energy",
        "attention": 94,
        "velocity": 88,
        "topic_slug": "ai-imperium-vs-energy-grid",
        "title": "AI Imperium vs Energy Grid",
        "video_type": "imperiumkriege",
        "template": "empire_map",
        "assets": ["ai_stocks", "utilities"],
        "asset_labels": ["AI Imperium", "Energy Grid"],
        "keywords": ["ai", "energy", "utilities", "technology"],
        "content_angle": "imperiumkriege",
        "risk_level": "medium",
        "default_period_days": 1095,
        "data_score": 78,
        "story_score": 96,
    },
    {
        "signal_id": "dollar-gold",
        "attention": 90,
        "velocity": 74,
        "topic_slug": "dollar-imperium-vs-gold-imperium",
        "title": "Dollar Imperium vs Gold Imperium",
        "video_type": "imperiumkriege",
        "template": "empire_map",
        "assets": ["dollar", "gold"],
        "asset_labels": ["Dollar Imperium", "Gold Imperium"],
        "keywords": ["dollar", "gold", "currency", "macro"],
        "content_angle": "imperiumkriege",
        "risk_level": "medium",
        "default_period_days": 1095,
        "data_score": 86,
        "story_score": 94,
    },
    {
        "signal_id": "oil-transport",
        "attention": 78,
        "velocity": 82,
        "topic_slug": "oil-imperium-vs-airline-imperium",
        "title": "Oil Imperium vs Airline Imperium",
        "video_type": "imperiumkriege",
        "template": "empire_map",
        "assets": ["oil", "airlines"],
        "asset_labels": ["Oil Imperium", "Airline Imperium"],
        "keywords": ["oil", "airlines", "fuel", "transport"],
        "content_angle": "imperiumkriege",
        "risk_level": "medium",
        "default_period_days": 1095,
        "data_score": 82,
        "story_score": 88,
    },
    {
        "signal_id": "chips-tech",
        "attention": 86,
        "velocity": 76,
        "topic_slug": "semiconductors-vs-nasdaq",
        "title": "Semiconductors vs Nasdaq",
        "video_type": "market_race",
        "template": "line_race",
        "assets": ["semiconductors", "nasdaq"],
        "asset_labels": ["Semiconductors", "Nasdaq"],
        "keywords": ["semiconductors", "nasdaq", "chips", "tech"],
        "content_angle": "comparison",
        "risk_level": "medium",
        "default_period_days": 1095,
        "data_score": 88,
        "story_score": 86,
    },
]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _recent(value: str | None, *, days: int, now: datetime) -> bool:
    parsed = parse_timestamp(value or "")
    return bool(parsed and parsed >= now - timedelta(days=days))


def _pair(assets: list[str]) -> str:
    return "+".join(sorted(normalize_slug(asset) for asset in assets))


def _score(history: list[dict[str, Any]], candidate: dict[str, Any], *, topic_days: int, pair_days: int, now: datetime) -> dict[str, Any]:
    hard: list[str] = []
    topic_key = normalize_slug(str(candidate["topic_slug"]))
    pair_key = _pair([str(asset) for asset in candidate["assets"]])
    for entry in history:
        created_at = str(entry.get("created_at", ""))
        if normalize_slug(str(entry.get("topic_slug", ""))) == topic_key and _recent(created_at, days=topic_days, now=now):
            hard.append(f"topic cooldown active for {topic_days} days")
        if _pair([str(asset) for asset in entry.get("asset_keys", [])]) == pair_key and _recent(created_at, days=pair_days, now=now):
            hard.append(f"asset pair cooldown active for {pair_days} days")
    base = round(candidate["attention"] * 0.38 + candidate["velocity"] * 0.24 + candidate["data_score"] * 0.18 + candidate["story_score"] * 0.20)
    return {
        **candidate,
        "base_score": base,
        "final_score": 0 if hard else base,
        "hard_blocked": bool(hard),
        "hard_block_reasons": sorted(set(hard)),
        "requires_review": True,
        "ready_to_publish": False,
    }


def _topic_brief(selected: dict[str, Any], *, job_id: str, generated_at: str) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "job_id": job_id,
        "run_mode": "trend_scan",
        "topic_id": selected["topic_slug"],
        "title": selected["title"],
        "hook": selected["title"],
        "video_type": selected["video_type"],
        "template": selected["template"],
        "assets": selected["assets"],
        "asset_labels": selected["asset_labels"],
        "keywords": selected["keywords"],
        "period_days": selected["default_period_days"],
        "locale": "de",
        "content_angle": selected["content_angle"],
        "risk_level": selected["risk_level"],
        "generated_at": generated_at,
        "trend_signal_id": selected["signal_id"],
        "trend_score": selected["final_score"],
        "requires_review": True,
        "ready_to_publish": False,
        "notes": ["Dry-run trend_scan selected from simulated T-2h signals.", "No live data was fetched."],
    }


def _sources(selected: dict[str, Any], *, job_id: str, generated_at: str) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "job_id": job_id,
        "generated_at": generated_at,
        "sources": [
            {
                "source_id": "simulated_trend_scan",
                "source_type": "local_dry_run",
                "name": "Simulated T-2h trend scan",
                "retrieved_at": generated_at,
                "selected_topic_slug": selected["topic_slug"],
                "limitations": ["No live trend data was fetched.", "No live market data was fetched."],
            }
        ],
    }


def _append_history(path: Path, *, selected: dict[str, Any], job_id: str, created_at: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "job_id": job_id,
        "created_at": created_at,
        "run_mode": "trend_scan",
        "video_type": selected["video_type"],
        "template": selected["template"],
        "topic_slug": selected["topic_slug"],
        "asset_keys": selected["assets"],
        "title": selected["title"],
        "trend_signal_id": selected["signal_id"],
        "trend_score": selected["final_score"],
        "qa_hard_fail": False,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def perform_research(*, job_id: str, out_dir: Path, history_path: Path, topic_days: int = 14, pair_days: int = 21, write_history: bool = True) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    generated_at = utc_now_iso()
    now = datetime.now(UTC).replace(microsecond=0)
    history = read_history(history_path)
    scored = [_score(history, candidate, topic_days=topic_days, pair_days=pair_days, now=now) for candidate in CANDIDATES]
    scored.sort(key=lambda item: (item["hard_blocked"], -int(item["final_score"]), str(item["topic_slug"])))
    report = {
        "contract_version": CONTRACT_VERSION,
        "job_id": job_id,
        "run_mode": "trend_scan",
        "generated_at": generated_at,
        "mode": "dry_run",
        "research_window": "prepublish_t_minus_2h",
        "candidate_count": len(scored),
        "top_candidate_slugs": [item["topic_slug"] for item in scored[:5]],
        "requires_review": True,
        "ready_to_publish": False,
        "limitations": ["Dry-run only: candidates are simulated.", "No live data was fetched."],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "trend_report.json", report)
    write_json(out_dir / "scored_candidates.json", scored)
    eligible = [item for item in scored if not item["hard_blocked"]]
    if not eligible:
        return None, scored
    selected = eligible[0]
    write_json(out_dir / "topic_brief.json", _topic_brief(selected, job_id=job_id, generated_at=generated_at))
    write_json(out_dir / "sources.json", _sources(selected, job_id=job_id, generated_at=generated_at))
    if write_history:
        _append_history(history_path, selected=selected, job_id=job_id, created_at=generated_at)
    return selected, scored
