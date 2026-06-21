"""CLI for ValueRacer QA dry-run checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .qa import evaluate_run, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qa_engine.cli",
        description="Evaluate ValueRacer dry-run artifacts and write qa.json.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Required safety flag. QA is currently dry-run only.")
    parser.add_argument("--run-dir", required=True, help="Run directory containing ValueRacer artifacts.")
    parser.add_argument("--history", default=None, help="Optional history JSONL path for repetition checks.")
    parser.add_argument(
        "--no-require-youtube",
        action="store_true",
        help="Do not fail when YouTube metadata or publish plan are missing.",
    )
    parser.add_argument("--out", default=None, help="Optional output path. Defaults to <run-dir>/qa.json.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.dry_run:
        print("error: --dry-run is required; production QA gates are not enabled yet", file=sys.stderr)
        return 2

    run_dir = Path(args.run_dir)
    if not run_dir.exists() or not run_dir.is_dir():
        print(f"error: run directory does not exist: {run_dir}", file=sys.stderr)
        return 1

    history_path = Path(args.history) if args.history else None
    qa_result = evaluate_run(
        run_dir,
        require_youtube=not args.no_require_youtube,
        history_path=history_path,
    )
    out_path = Path(args.out) if args.out else run_dir / "qa.json"
    write_json(out_path, qa_result)

    print(json.dumps(qa_result, indent=2, ensure_ascii=False))
    return 1 if qa_result.get("hard_fail") else 0


if __name__ == "__main__":
    raise SystemExit(main())
