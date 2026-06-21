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
    return parser


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
    except OSError as exc:
        print(f"error: failed to create dry-run job: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
