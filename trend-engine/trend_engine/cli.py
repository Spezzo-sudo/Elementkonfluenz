"""CLI for ValueRacer trend-engine dry-runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import (
    DEFAULT_CATALOG_PATH,
    append_history,
    build_sources,
    build_topic_brief,
    choose_candidate,
    load_catalog,
    read_history,
    utc_now_iso,
    write_json,
)
from .research import perform_research


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trend_engine.cli",
        description="Select the next ValueRacer topic with cooldown protection.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Required safety flag. No live data is fetched.")
    parser.add_argument("--mode", default="market_scan", choices=["market_scan", "trend_scan"], help="Trend engine mode.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG_PATH), help="Path to topic catalog JSON for market_scan.")
    parser.add_argument("--history", default="runs/history.jsonl", help="Run history JSONL used for cooldown checks.")
    parser.add_argument("--out", required=True, help="Output path for topic_brief.json.")
    parser.add_argument("--sources-out", required=True, help="Output path for sources.json.")
    parser.add_argument("--job-id", default=None, help="Optional job id. Defaults to the output run directory name.")
    parser.add_argument("--cooldown-days", type=int, default=14, help="Topic cooldown in days.")
    parser.add_argument("--asset-pair-cooldown-days", type=int, default=21, help="Asset-pair cooldown in days.")
    parser.add_argument("--max-same-video-type-in-row", type=int, default=2, help="Consecutive video-type limit for market_scan.")
    parser.add_argument("--max-same-template-in-row", type=int, default=2, help="Consecutive template limit for market_scan.")
    parser.add_argument("--write-history", action="store_true", help="Append the selected topic to the history JSONL file.")
    return parser


def resolve_job_id(args: argparse.Namespace) -> str:
    if args.job_id:
        return str(args.job_id)
    out_path = Path(args.out)
    if out_path.parent.name:
        return out_path.parent.name
    return f"{args.mode}-dry-run"


def validate_args(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    if not args.dry_run:
        errors.append("--dry-run is required; live scans are not implemented")
    if args.cooldown_days < 0:
        errors.append("--cooldown-days must be >= 0")
    if args.asset_pair_cooldown_days < 0:
        errors.append("--asset-pair-cooldown-days must be >= 0")
    if args.max_same_video_type_in_row < 1:
        errors.append("--max-same-video-type-in-row must be >= 1")
    if args.max_same_template_in_row < 1:
        errors.append("--max-same-template-in-row must be >= 1")
    return errors


def run_market_scan(args: argparse.Namespace, *, job_id: str) -> int:
    catalog_path = Path(args.catalog)
    history_path = Path(args.history)
    topic_out = Path(args.out)
    sources_out = Path(args.sources_out)
    generated_at = utc_now_iso()

    candidates = load_catalog(catalog_path)
    history = read_history(history_path)
    selected, rejected = choose_candidate(
        candidates,
        history,
        topic_cooldown_days=args.cooldown_days,
        asset_pair_cooldown_days=args.asset_pair_cooldown_days,
        max_same_video_type_in_row=args.max_same_video_type_in_row,
        max_same_template_in_row=args.max_same_template_in_row,
    )

    if selected is None:
        result = {
            "ok": False,
            "stage": "trend-engine",
            "job_id": job_id,
            "error_code": "NO_ELIGIBLE_TOPIC",
            "message": "No catalog topic passed cooldown and rotation checks.",
            "retryable": True,
            "requires_review": True,
            "ready_to_publish": False,
            "rejected_candidates": rejected,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

    topic_brief = build_topic_brief(selected, job_id=job_id, generated_at=generated_at)
    sources = build_sources(selected, job_id=job_id, generated_at=generated_at, rejected=rejected)
    write_json(topic_out, topic_brief)
    write_json(sources_out, sources)

    if args.write_history:
        append_history(history_path, candidate=selected, job_id=job_id, created_at=generated_at)

    result = {
        "ok": True,
        "stage": "trend-engine",
        "job_id": job_id,
        "mode": "dry_run",
        "run_mode": "market_scan",
        "selected_topic_slug": selected.topic_slug,
        "video_type": selected.video_type,
        "template": selected.template,
        "artifacts": [str(topic_out), str(sources_out)],
        "warnings": ["Dry-run only: no live data was fetched."],
        "requires_review": True,
        "ready_to_publish": False,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def run_trend_scan(args: argparse.Namespace, *, job_id: str) -> int:
    topic_out = Path(args.out)
    sources_out = Path(args.sources_out)
    out_dir = topic_out.parent
    selected, scored = perform_research(
        job_id=job_id,
        out_dir=out_dir,
        history_path=Path(args.history),
        topic_days=args.cooldown_days,
        pair_days=args.asset_pair_cooldown_days,
        write_history=args.write_history,
    )
    if topic_out != out_dir / "topic_brief.json" and (out_dir / "topic_brief.json").exists():
        topic_out.write_text((out_dir / "topic_brief.json").read_text(encoding="utf-8"), encoding="utf-8")
    if sources_out != out_dir / "sources.json" and (out_dir / "sources.json").exists():
        sources_out.write_text((out_dir / "sources.json").read_text(encoding="utf-8"), encoding="utf-8")
    if selected is None:
        result = {
            "ok": False,
            "stage": "trend-engine",
            "job_id": job_id,
            "error_code": "NO_ELIGIBLE_TREND_CANDIDATE",
            "message": "No simulated trend candidate passed cooldown checks.",
            "retryable": True,
            "requires_review": True,
            "ready_to_publish": False,
            "scored_candidates": scored,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1
    result = {
        "ok": True,
        "stage": "trend-engine",
        "job_id": job_id,
        "mode": "dry_run",
        "run_mode": "trend_scan",
        "selected_topic_slug": selected["topic_slug"],
        "video_type": selected["video_type"],
        "template": selected["template"],
        "artifacts": [str(topic_out), str(sources_out), str(out_dir / "trend_report.json"), str(out_dir / "scored_candidates.json")],
        "warnings": ["Dry-run only: trend_scan uses simulated T-2h signals."],
        "requires_review": True,
        "ready_to_publish": False,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    errors = validate_args(args)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 2
    job_id = resolve_job_id(args)
    try:
        if args.mode == "trend_scan":
            return run_trend_scan(args, job_id=job_id)
        return run_market_scan(args, job_id=job_id)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: trend-engine failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
