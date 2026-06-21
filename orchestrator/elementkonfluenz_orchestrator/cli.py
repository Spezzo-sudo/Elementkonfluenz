"""CLI entry point for the Hermes-compatible ValueRacer dry-run orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .job import create_dry_run_job, default_job_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="valueracer_orchestrator.cli",
        description="Create a Hermes-compatible ValueRacer dry-run job folder.",
    )
    parser.add_argument("--topic", required=True, help="Human-readable topic title, e.g. 'Gold vs S&P 500'.")
    parser.add_argument("--out", required=False, help="Output run directory. Defaults to runs/<generated-job-id>.")
    parser.add_argument("--job-id", default=None, help="Optional explicit job id. Defaults to timestamp + topic slug.")
    parser.add_argument("--locale", default="de", help="Topic locale. Defaults to de.")
    parser.add_argument("--period-days", type=int, default=1825, help="Lookback period placeholder for the topic brief.")
    parser.add_argument("--dry-run", action="store_true", help="Required safety flag. No publish-capable mode exists yet.")
    parser.add_argument(
        "--with-youtube-seo",
        action="store_true",
        help="Also generate dry-run YouTube metadata and publish-plan artifacts. Requires valueracer_seo to be installed.",
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.dry_run:
        print("error: --dry-run is required; publish-capable orchestration is intentionally not implemented", file=sys.stderr)
        return 2

    if args.period_days < 1:
        print("error: --period-days must be >= 1", file=sys.stderr)
        return 2

    job_id = args.job_id or default_job_id(args.topic)
    out_dir = Path(args.out) if args.out else Path("runs") / job_id

    try:
        result = create_dry_run_job(
            topic=args.topic,
            out_dir=out_dir,
            job_id=job_id,
            locale=args.locale,
            period_days=args.period_days,
        )

        if args.with_youtube_seo:
            seo_result = run_youtube_seo_dry_run(out_dir)
            result.artifacts.extend(artifact for artifact in seo_result.get("artifacts", []) if artifact not in result.artifacts)
            result.warnings.extend(seo_result.get("warnings", []))
            result.message = "Dry-run job folder created and YouTube SEO artifacts generated successfully."
            result.requires_review = True
            result.ready_to_publish = False
            result.write(out_dir / "job_result.json")
            with (out_dir / "logs" / "orchestrator.log").open("a", encoding="utf-8") as log_file:
                log_file.write("generated YouTube SEO dry-run artifacts\n")
    except ModuleNotFoundError as exc:
        if args.with_youtube_seo and exc.name and exc.name.startswith("valueracer_seo"):
            print("error: --with-youtube-seo requires the seo-engine package to be installed", file=sys.stderr)
            return 2
        print(f"error: missing required module: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: failed to create dry-run job: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
