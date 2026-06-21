"""YouTube metadata and publish-plan generation for ValueRacer dry-runs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "0.1"
DEFAULT_CATEGORY_ID = "25"
DEFAULT_LANGUAGE = "de"

ADVISORY_KEYWORDS = [
    "kaufen",
    "verkaufen",
    "jetzt einsteigen",
    "garantierter gewinn",
    "sichere rendite",
    "kein risiko",
    "all in",
    "reich werden",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_words(value: str) -> list[str]:
    return [word for word in re.split(r"[^A-Za-z0-9ÄÖÜäöüß]+", value.lower()) if word]


def build_tags(topic_brief: dict[str, Any]) -> list[str]:
    title = str(topic_brief.get("title") or topic_brief.get("hook") or "ValueRacer")
    assets = [str(asset).lower() for asset in topic_brief.get("assets", []) if str(asset).strip()]
    words = normalize_words(title)
    base = ["valueracer", "wirtschaft", "finanzen"]
    tags: list[str] = []

    for item in [*assets, *words, *base]:
        normalized = item.strip().lower().replace("#", "")
        if normalized and normalized not in tags:
            tags.append(normalized)

    return tags[:12]


def build_title(topic_brief: dict[str, Any]) -> str:
    title = str(topic_brief.get("title") or topic_brief.get("hook") or "ValueRacer Marktvergleich").strip()
    if len(title) <= 82:
        return title
    return title[:79].rstrip() + "..."


def build_thumbnail_text(title: str) -> str:
    words = [word for word in re.split(r"\s+", title.strip()) if word]
    if not words:
        return "ValueRacer"
    return " ".join(words[:4])[:32]


def build_description(topic_brief: dict[str, Any], sources: dict[str, Any] | None) -> str:
    title = str(topic_brief.get("title") or "dieses Thema")
    period_days = topic_brief.get("period_days")
    period_text = f" ueber einen Zeitraum von {period_days} Tagen" if period_days else " ueber den angegebenen Zeitraum"
    source_note = "Datenstand und Quellen werden im Quellenmanifest des Runs gespeichert."
    if sources and sources.get("sources"):
        source_note = "Quellen und Einschraenkungen sind im sources.json dieses Runs dokumentiert."

    return "\n".join(
        [
            f"In diesem Video ordnet ValueRacer {title}{period_text} ein.",
            "Ziel ist keine Prognose und keine Anlageberatung, sondern ein datenbasierter Vergleich mit klarer Einordnung.",
            source_note,
            "",
            "#Shorts #Wirtschaft #Finanzen",
        ]
    )


def advisory_check(*texts: str) -> dict[str, Any]:
    haystack = "\n".join(texts).lower()
    matches = [keyword for keyword in ADVISORY_KEYWORDS if keyword in haystack]
    return {
        "flagged": bool(matches),
        "matched_keywords": matches,
        "suggestions": ["Formuliere als Datenvergleich statt Handlungsempfehlung."] if matches else [],
    }


def build_youtube_metadata(
    *,
    job_id: str,
    topic_brief: dict[str, Any],
    sources: dict[str, Any] | None,
) -> dict[str, Any]:
    title = build_title(topic_brief)
    description = build_description(topic_brief, sources)
    tags = build_tags(topic_brief)
    hashtags = ["#Shorts", "#Wirtschaft", "#Finanzen"]
    thumbnail_text = build_thumbnail_text(title)
    check = advisory_check(title, description, thumbnail_text)

    return {
        "contract_version": CONTRACT_VERSION,
        "platform": "youtube",
        "job_id": job_id,
        "title": title,
        "description": description,
        "tags": tags,
        "hashtags": hashtags,
        "thumbnail_text": thumbnail_text,
        "default_language": DEFAULT_LANGUAGE,
        "category_id": DEFAULT_CATEGORY_ID,
        "made_for_kids": False,
        "contains_synthetic_media": True,
        "source_disclaimer": "Datenstand und Quellen siehe sources.json im Run-Ordner.",
        "advisory_check": check,
        "clickbait_integrity_check": {
            "passed": not check["flagged"],
            "reason": "Titel und Thumbnail sind als neugieriger Datenvergleich formuliert, nicht als Kauf- oder Gewinnversprechen.",
        },
        "requires_review": True,
    }


def build_youtube_publish_plan(
    *,
    job_id: str,
    video_file: str,
    thumbnail_file: str | None,
    caption_file: str | None,
) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "platform": "youtube",
        "mode": "dry_run",
        "job_id": job_id,
        "video_file": video_file,
        "thumbnail_file": thumbnail_file,
        "caption_file": caption_file,
        "metadata_file": "metadata/youtube.json",
        "privacy_status": "private",
        "publish_at": None,
        "notify_subscribers": False,
        "made_for_kids": False,
        "contains_synthetic_media": True,
        "requires_review": True,
        "ready_to_publish": False,
        "warnings": [
            "Dry-run only: no YouTube API call was made.",
            "Default privacy remains private.",
        ],
    }


def generate_youtube_dry_run(
    *,
    run_dir: Path,
    topic_brief_path: Path,
    sources_path: Path | None,
    video_file: str = "render.mp4",
    thumbnail_file: str | None = None,
    caption_file: str | None = None,
) -> dict[str, Any]:
    topic_brief = read_json(topic_brief_path)
    sources = read_json(sources_path) if sources_path and sources_path.exists() else None
    job_id = str(topic_brief.get("job_id") or topic_brief.get("topic_id") or run_dir.name)

    metadata = build_youtube_metadata(job_id=job_id, topic_brief=topic_brief, sources=sources)
    publish_plan = build_youtube_publish_plan(
        job_id=job_id,
        video_file=video_file,
        thumbnail_file=thumbnail_file,
        caption_file=caption_file,
    )

    write_json(run_dir / "metadata" / "youtube.json", metadata)
    write_json(run_dir / "publish" / "youtube_publish_plan.json", publish_plan)

    return {
        "ok": True,
        "stage": "seo",
        "job_id": job_id,
        "artifacts": [
            "metadata/youtube.json",
            "publish/youtube_publish_plan.json",
        ],
        "warnings": [
            "Dry-run only: no YouTube API call was made.",
            "Metadata requires manual review before publishing.",
        ],
        "requires_review": True,
        "ready_to_publish": False,
    }
