"""CLI entry point for the Hermes-compatible ValueRacer dry-run orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .job import create_dry_run_job, default_job_id, utc_now_iso
from .result import JobResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="valueracer_orchestrator.cli",
        description="Create a Hermes-compatible ValueRacer dry-run job folder.",
    )
    parser.add_argument(
        "--run-mode",
        default="manual_topic",
        choices=["manual_topic", "market_scan", "trend_scan"],
        help="Run mode. manual_topic uses --topic; market_scan selects from the catalog; trend_scan selects from simulated prepublish research.",
    )
    parser.add_argument("--topic", required=False, help="Human-readable topic title, e.g. 'Gold vs S&P 500'. Required for manual_topic.")
    parser.add_argument("--out", required=False, help="Output run directory. Defaults to runs/<generated-job-id>.")
    parser.add_argument("--job-id", default=None, help="Optional explicit job id. Defaults to timestamp + topic/run-mode slug.")
    parser.add_argument("--locale", default="de", help="Topic locale. Defaults to de.")
    parser.add_argument("--period-days", type=int, default=1825, help="Lookback period placeholder for manual_topic topic briefs.")
    parser.add_argument("--dry-run", action="store_true", help="Required safety flag. No publish-capable mode exists yet.")
    parser.add_argument("--history", default=None, help="History JSONL path for scan modes/QA. Defaults to <runs-dir>/history.jsonl.")
    parser.add_argument("--cooldown-days", type=int, default=14, help="Topic cooldown in days for scan modes.")
    parser.add_argument("--asset-pair-cooldown-days", type=int, default=21, help="Asset-pair cooldown in days for scan modes.")
    parser.add_argument("--max-same-video-type-in-row", type=int, default=2, help="Consecutive video-type limit for market_scan.")
    parser.add_argument("--max-same-template-in-row", type=int, default=2, help="Consecutive template limit for market_scan.")
    parser.add_argument(
        "--skip-history-write",
        action="store_true",
        help="Do not append the selected scan topic to history. Useful for throwaway tests.",
    )
    parser.add_argument(
        "--with-youtube-seo",
        action="store_true",
        help="Also generate dry-run YouTube metadata and publish-plan artifacts. Requires valueracer_seo to be installed.",
    )
    parser.add_argument(
        "--with-qa",
        action="store_true",
        help="Also run dry-run QA gates and write qa.json. Requires qa-engine to be installed.",
    )
    parser.add_argument(
        "--qa-no-require-youtube",
        action="store_true",
        help="When --with-qa is used, do not fail QA if YouTube artifacts are missing.",
    )
    return parser


def run_youtube_seo_dry_run(out_dir: Path) -> dict:
    """Run the optional YouTube SEO dry-run stage.

    The import is intentionally lazy so the base orchestrator can still run without the SEO package.
    """
    from valueracer_seo.youtube import generate_youtube_dry_run

    return generate_youtube_dry_run(
        run_dir=out_dir,
        topic_brief_path=out_dir / "topic_brief.json",
        sources_path=out_dir / "sources.json",
    )


def resolve_history_path(args: argparse.Namespace, out_dir: Path) -> Path:
    runs_dir = out_dir.parent
    return Path(args.history) if args.history else runs_dir / "history.jsonl"


def run_qa_dry_run(args: argparse.Namespace, *, out_dir: Path) -> dict:
    """Run the optional QA dry-run stage and write qa.json.

    The import is intentionally lazy so the base orchestrator can still run without the QA package.
    """
    from qa_engine.qa import evaluate_run, write_json

    history_path = resolve_history_path(args, out_dir)
    qa_result = evaluate_run(
        out_dir,
        require_youtube=not args.qa_no_require_youtube,
        history_path=history_path if history_path.exists() else None,
    )
    write_json(out_dir / "qa.json", qa_result)
    return qa_result


def run_market_scan_dry_run(args: argparse.Namespace, *, out_dir: Path, job_id: str) -> JobResult:
    """Select a catalog topic via trend-engine and create the initial run folder."""
    from trend_engine.catalog import (
        DEFAULT_CATALOG_PATH,
        append_history,
        build_sources,
        build_topic_brief,
        choose_candidate,
        load_catalog,
        read_history,
        write_json,
    )

    generated_at = utc_now_iso()
    out_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = out_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    history_path = resolve_history_path(args, out_dir)
    candidates = load_catalog(DEFAULT_CATALOG_PATH)
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
        message = "No catalog topic passed cooldown and rotation checks."
        result = JobResult(
            job_id=job_id,
            ok=False,
            stage="trend-engine",
            artifacts=["job_result.json", "logs/orchestrator.log"],
            warnings=[message],
            message=message,
            retryable=True,
            error_code="NO_ELIGIBLE_TOPIC",
            requires_review=True,
            ready_to_publish=False,
        )
        result.write(out_dir / "job_result.json")
        (logs_dir / "orchestrator.log").write_text(
            "\n".join(
                [
                    f"{generated_at} market_scan dry-run started",
                    f"job_id={job_id}",
                    "no eligible topic selected",
                    json.dumps({"rejected_candidates": rejected}, ensure_ascii=False),
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return result

    topic_brief = build_topic_brief(selected, job_id=job_id, generated_at=generated_at)
    sources = build_sources(selected, job_id=job_id, generated_at=generated_at, rejected=rejected)
    write_json(out_dir / "topic_brief.json", topic_brief)
    write_json(out_dir / "sources.json", sources)

    if not args.skip_history_write:
        append_history(history_path, candidate=selected, job_id=job_id, created_at=generated_at)

    log_text = "\n".join(
        [
            f"{generated_at} market_scan dry-run started",
            f"job_id={job_id}",
            f"selected_topic_slug={selected.topic_slug}",
            f"video_type={selected.video_type}",
            f"template={selected.template}",
            f"history_path={history_path}",
            "wrote topic_brief.json",
            "wrote sources.json",
            "wrote job_result.json",
            "no render, distribution, or publish step executed",
            "",
        ]
    )
    (logs_dir / "orchestrator.log").write_text(log_text, encoding="utf-8")

    result = JobResult(
        job_id=job_id,
        ok=True,
        stage="orchestrator",
        artifacts=[
            "topic_brief.json",
            "sources.json",
            "job_result.json",
            "logs/orchestrator.log",
        ],
        warnings=[
            "Dry-run only: market_scan selected a static catalog topic; no live market data was fetched.",
            "A later data QA stage must validate all market values before rendering.",
        ],
        message=f"Market-scan dry-run selected topic: {selected.title}.",
        requires_review=True,
        ready_to_publish=False,
    )
    result.write(out_dir / "job_result.json")
    return result


def run_trend_scan_dry_run(args: argparse.Namespace, *, out_dir: Path, job_id: str) -> JobResult:
    """Select a topic via trend-engine research and create the initial run folder."""
    from .trend_scan import run_trend_scan_dry_run as run_helper

    return run_helper(args, out_dir=out_dir, job_id=job_id, history_path=resolve_history_path(args, out_dir))


def validate_args(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    if not args.dry_run:
        errors.append("--dry-run is required; publish-capable orchestration is intentionally not implemented")
    if args.run_mode == "manual_topic" and not args.topic:
        errors.append("--topic is required when --run-mode manual_topic")
    if args.qa_no_require_youtube and not args.with_qa:
        errors.append("--qa-no-require-youtube requires --with-qa")
    if args.period_days < 1:
        errors.append("--period-days must be >= 1")
    if args.cooldown_days < 0:
        errors.append("--cooldown-days must be >= 0")
    if args.asset_pair_cooldown_days < 0:
        errors.append("--asset-pair-cooldown-days must be >= 0")
    if args.max_same_video_type_in_row < 1:
        errors.append("--max-same-video-type-in-row must be >= 1")
    if args.max_same_template_in_row < 1:
        errors.append("--max-same-template-in-row must be >= 1")
    return errors


def resolve_job_id(args: argparse.Namespace) -> str:
    if args.job_id:
        return str(args.job_id)
    if args.run_mode == "manual_topic":
        return default_job_id(str(args.topic))
    return default_job_id(args.run_mode.replace("_", "-"))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    errors = validate_args(args)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 2

    job_id = resolve_job_id(args)
    out_dir = Path(args.out) if args.out else Path("runs") / job_id

    try:
        if args.run_mode == "manual_topic":
            result = create_dry_run_job(
                topic=str(args.topic),
                out_dir=out_dir,
                job_id=job_id,
                locale=args.locale,
                period_days=args.period_days,
            )
        elif args.run_mode == "market_scan":
            result = run_market_scan_dry_run(args, out_dir=out_dir, job_id=job_id)
        else:
            result = run_trend_scan_dry_run(args, out_dir=out_dir, job_id=job_id)

        if args.with_youtube_seo and result.ok:
            seo_result = run_youtube_seo_dry_run(out_dir)
            result.artifacts.extend(artifact for artifact in seo_result.get("artifacts", []) if artifact not in result.artifacts)
            result.warnings.extend(seo_result.get("warnings", []))
            result.message = "Dry-run job folder created and YouTube SEO artifacts generated successfully."
            result.requires_review = True
            result.ready_to_publish = False
            result.write(out_dir / "job_result.json")
            with (out_dir / "logs" / "orchestrator.log").open("a", encoding="utf-8") as log_file:
                log_file.write("generated YouTube SEO dry-run artifacts\n")

        if args.with_qa and result.ok:
            qa_result = run_qa_dry_run(args, out_dir=out_dir)
            if "qa.json" not in result.artifacts:
                result.artifacts.append("qa.json")
            qa_warnings = qa_result.get("warnings", [])
            result.warnings.extend(warning for warning in qa_warnings if warning not in result.warnings)
            if qa_result.get("hard_fail"):
                result.ok = False
                result.stage = "qa"
                result.error_code = "QA_HARD_FAIL"
                result.message = "Dry-run QA completed with hard_fail=true. Review required before any further step."
            else:
                result.message = "Dry-run job folder created, YouTube SEO artifacts generated, and QA passed."
            result.requires_review = True
            result.ready_to_publish = False
            result.write(out_dir / "job_result.json")
            with (out_dir / "logs" / "orchestrator.log").open("a", encoding="utf-8") as log_file:
                log_file.write("generated QA dry-run artifact\n")
    except ModuleNotFoundError as exc:
        if args.with_youtube_seo and exc.name and exc.name.startswith("valueracer_seo"):
            print("error: --with-youtube-seo requires the seo-engine package to be installed", file=sys.stderr)
            return 2
        if args.run_mode in {"market_scan", "trend_scan"} and exc.name and exc.name.startswith("trend_engine"):
            print("error: scan run modes require the trend-engine package to be installed", file=sys.stderr)
            return 2
        if args.with_qa and exc.name and exc.name.startswith("qa_engine"):
            print("error: --with-qa requires the qa-engine package to be installed", file=sys.stderr)
            return 2
        print(f"error: missing required module: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: failed to create dry-run job: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 1 if not result.ok else 0


if __name__ == "__main__":
    raise SystemExit(main())
