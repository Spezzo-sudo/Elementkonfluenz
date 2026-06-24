"""Trend-scan helper for the ValueRacer orchestrator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .job import utc_now_iso
from .result import JobResult


def run_trend_scan_dry_run(args: Any, *, out_dir: Path, job_id: str, history_path: Path) -> JobResult:
    """Create a dry-run folder from trend_engine.research.perform_research."""
    from trend_engine.research import perform_research

    generated_at = utc_now_iso()
    out_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = out_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    selected, scored = perform_research(
        job_id=job_id,
        out_dir=out_dir,
        history_path=history_path,
        topic_days=args.cooldown_days,
        pair_days=args.asset_pair_cooldown_days,
        write_history=not args.skip_history_write,
    )

    if selected is None:
        message = "No trend candidate passed cooldown checks."
        result = JobResult(
            job_id=job_id,
            ok=False,
            stage="trend-engine",
            artifacts=["trend_report.json", "scored_candidates.json", "job_result.json", "logs/orchestrator.log"],
            warnings=[message],
            message=message,
            retryable=True,
            error_code="NO_ELIGIBLE_TREND_CANDIDATE",
            requires_review=True,
            ready_to_publish=False,
        )
        result.write(out_dir / "job_result.json")
        (logs_dir / "orchestrator.log").write_text(
            "\n".join([
                f"{generated_at} trend_scan dry-run started",
                f"job_id={job_id}",
                "no eligible trend candidate selected",
                json.dumps({"scored_candidates": scored}, ensure_ascii=False),
                "",
            ]),
            encoding="utf-8",
        )
        return result

    (logs_dir / "orchestrator.log").write_text(
        "\n".join([
            f"{generated_at} trend_scan dry-run started",
            f"job_id={job_id}",
            f"selected_topic_slug={selected['topic_slug']}",
            f"video_type={selected['video_type']}",
            f"template={selected['template']}",
            "wrote trend_report.json",
            "wrote scored_candidates.json",
            "wrote topic_brief.json",
            "wrote sources.json",
            "wrote job_result.json",
            "no render, distribution, or platform step executed",
            "",
        ]),
        encoding="utf-8",
    )

    result = JobResult(
        job_id=job_id,
        ok=True,
        stage="orchestrator",
        artifacts=[
            "trend_report.json",
            "scored_candidates.json",
            "topic_brief.json",
            "sources.json",
            "job_result.json",
            "logs/orchestrator.log",
        ],
        warnings=[
            "Dry-run only: trend_scan uses simulated T-2h signals.",
            "Live source validation is required before rendering or platform steps.",
        ],
        message=f"Trend-scan dry-run selected topic: {selected['title']}.",
        requires_review=True,
        ready_to_publish=False,
    )
    result.write(out_dir / "job_result.json")
    return result
