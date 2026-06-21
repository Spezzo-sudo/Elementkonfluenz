"""Topic catalog selection with cooldown protection for ValueRacer dry-runs."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "0.1"
DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "topic_catalog.json"
_SAFE_SLUG_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class TopicCandidate:
    topic_slug: str
    title: str
    video_type: str
    template: str
    assets: list[str]
    asset_labels: list[str]
    keywords: list[str]
    content_angle: str
    risk_level: str
    default_period_days: int
    priority: int

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TopicCandidate":
        return cls(
            topic_slug=str(payload["topic_slug"]),
            title=str(payload["title"]),
            video_type=str(payload.get("video_type", "market_race")),
            template=str(payload.get("template", "bar_race")),
            assets=[str(item) for item in payload.get("assets", [])],
            asset_labels=[str(item) for item in payload.get("asset_labels", [])],
            keywords=[str(item) for item in payload.get("keywords", [])],
            content_angle=str(payload.get("content_angle", "comparison")),
            risk_level=str(payload.get("risk_level", "medium")),
            default_period_days=int(payload.get("default_period_days", 1825)),
            priority=int(payload.get("priority", 0)),
        )

    @property
    def asset_pair_key(self) -> str:
        return "+".join(sorted(normalize_slug(asset) for asset in self.assets))


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def utc_now_iso() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def normalize_slug(value: str) -> str:
    lowered = value.strip().lower()
    slug = _SAFE_SLUG_RE.sub("-", lowered).strip("-")
    return slug or "unknown"


def load_catalog(path: Path) -> list[TopicCandidate]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [TopicCandidate.from_dict(item) for item in payload.get("topics", [])]


def read_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            entries.append(json.loads(stripped))
        except json.JSONDecodeError:
            entries.append({"invalid_history_line": stripped})
    return entries


def parse_timestamp(value: str) -> datetime | None:
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except (TypeError, ValueError):
        return None


def is_recent(timestamp: str | None, *, days: int, now: datetime) -> bool:
    if not timestamp:
        return False
    parsed = parse_timestamp(timestamp)
    if parsed is None:
        return False
    return parsed >= now - timedelta(days=days)


def cooldown_reasons(
    candidate: TopicCandidate,
    history: list[dict[str, Any]],
    *,
    topic_cooldown_days: int,
    asset_pair_cooldown_days: int,
    max_same_video_type_in_row: int,
    max_same_template_in_row: int,
    now: datetime,
) -> list[str]:
    reasons: list[str] = []
    topic_slug = normalize_slug(candidate.topic_slug)
    asset_pair_key = candidate.asset_pair_key

    for entry in history:
        created_at = str(entry.get("created_at", ""))
        if normalize_slug(str(entry.get("topic_slug", ""))) == topic_slug and is_recent(
            created_at, days=topic_cooldown_days, now=now
        ):
            reasons.append(f"topic cooldown active for {topic_cooldown_days} days")
            break

    for entry in history:
        created_at = str(entry.get("created_at", ""))
        entry_assets = entry.get("asset_keys", [])
        entry_pair = "+".join(sorted(normalize_slug(str(asset)) for asset in entry_assets))
        if entry_pair == asset_pair_key and is_recent(created_at, days=asset_pair_cooldown_days, now=now):
            reasons.append(f"asset pair cooldown active for {asset_pair_cooldown_days} days")
            break

    recent_valid_entries = [entry for entry in history if "invalid_history_line" not in entry]
    recent_valid_entries = list(reversed(recent_valid_entries))

    same_video_type_count = 0
    for entry in recent_valid_entries:
        if entry.get("video_type") == candidate.video_type:
            same_video_type_count += 1
        else:
            break
    if same_video_type_count >= max_same_video_type_in_row:
        reasons.append(f"video type rotation blocked after {same_video_type_count} consecutive runs")

    same_template_count = 0
    for entry in recent_valid_entries:
        if entry.get("template") == candidate.template:
            same_template_count += 1
        else:
            break
    if same_template_count >= max_same_template_in_row:
        reasons.append(f"template rotation blocked after {same_template_count} consecutive runs")

    return reasons


def choose_candidate(
    candidates: list[TopicCandidate],
    history: list[dict[str, Any]],
    *,
    topic_cooldown_days: int = 14,
    asset_pair_cooldown_days: int = 21,
    max_same_video_type_in_row: int = 2,
    max_same_template_in_row: int = 2,
    now: datetime | None = None,
) -> tuple[TopicCandidate | None, list[dict[str, Any]]]:
    now = now or utc_now()
    sorted_candidates = sorted(candidates, key=lambda item: item.priority, reverse=True)
    rejected: list[dict[str, Any]] = []

    for candidate in sorted_candidates:
        reasons = cooldown_reasons(
            candidate,
            history,
            topic_cooldown_days=topic_cooldown_days,
            asset_pair_cooldown_days=asset_pair_cooldown_days,
            max_same_video_type_in_row=max_same_video_type_in_row,
            max_same_template_in_row=max_same_template_in_row,
            now=now,
        )
        if not reasons:
            return candidate, rejected
        rejected.append({"topic_slug": candidate.topic_slug, "reasons": reasons})

    return None, rejected


def build_topic_brief(candidate: TopicCandidate, *, job_id: str, generated_at: str) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "job_id": job_id,
        "run_mode": "market_scan",
        "topic_id": candidate.topic_slug,
        "title": candidate.title,
        "hook": candidate.title,
        "video_type": candidate.video_type,
        "template": candidate.template,
        "assets": candidate.assets,
        "asset_labels": candidate.asset_labels,
        "keywords": candidate.keywords,
        "period_days": candidate.default_period_days,
        "locale": "de",
        "content_angle": candidate.content_angle,
        "risk_level": candidate.risk_level,
        "generated_at": generated_at,
        "requires_review": True,
        "ready_to_publish": False,
        "notes": [
            "Dry-run market_scan topic selected from static catalog.",
            "No external market data was fetched yet.",
            "Trend and data checks must be added before production use.",
        ],
    }


def build_sources(candidate: TopicCandidate, *, job_id: str, generated_at: str, rejected: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "job_id": job_id,
        "generated_at": generated_at,
        "sources": [
            {
                "source_id": "static_topic_catalog",
                "source_type": "local_catalog",
                "name": "ValueRacer static topic catalog",
                "retrieved_at": generated_at,
                "topics_considered": len(rejected) + 1,
                "selected_topic_slug": candidate.topic_slug,
                "limitations": [
                    "This dry-run does not fetch live market data.",
                    "Catalog priority and cooldown are used only for safe topic selection.",
                    "A later data stage must validate all market values before rendering.",
                ],
            }
        ],
        "rejected_candidates": rejected,
    }


def append_history(path: Path, *, candidate: TopicCandidate, job_id: str, created_at: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "job_id": job_id,
        "created_at": created_at,
        "run_mode": "market_scan",
        "video_type": candidate.video_type,
        "template": candidate.template,
        "topic_slug": candidate.topic_slug,
        "asset_keys": candidate.assets,
        "title": candidate.title,
        "qa_hard_fail": False,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
