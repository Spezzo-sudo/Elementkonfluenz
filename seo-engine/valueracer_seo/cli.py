"""CLI for ValueRacer SEO dry-runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .youtube import generate_youtube_dry_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="valueracer_seo.cli",
        description="Generate ValueRacer YouTube metadata and publish plan in dry-run mode.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Required safety flag. No publish-capable mode exists yet.")
    parser.add_argument("--run-dir", help="Run directory containing topic_brief.json and optionally sources.json.")
    parser.add_argument("--topic-brief", help="Path to topic_brief.json. Defaults to <run-dir>/topic_brief.json.")
    parser.add_argument("--sources", help="Optional path to sources.json. Defaults to <run-dir>/sources.json when present.")
    parser.add_argument("--out-dir", help="Output run directory. Defaults to --run-dir.")
    parser.add_argument("--video-file", default="render.mp4", help="Video file path relative to the run directory.")
    parser.add_argument("--thumbnail-file", default=None, help="Optional thumbnail file path relative to the run directory.")
    parser.add_argument("--caption-file", default=None, help="Optional caption file path relative to the run directory.")
    return parser


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path, Path | None]:
    if not args.run_dir and not args.topic_brief:
        raise ValueError("Either --run-dir or --topic-brief is required.")

    run_dir = Path(args.out_dir or args.run_dir or Path(args.topic_brief).parent)
    topic_brief_path = Path(args.topic_brief) if args.topic_brief else run_dir / "topic_brief.json"

    if args.sources:
        sources_path: Path | None = Path(args.sources)
    else:
        candidate = run_dir / "sources.json"
        sources_path = candidate if candidate.exists() else None

    return run_dir, topic_brief_path, sources_path


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.dry_run:
        print("error: --dry-run is required; publish-capable SEO is intentionally not implemented", file=sys.stderr)
        return 2

    try:
        run_dir, topic_brief_path, sources_path = resolve_paths(args)
        if not topic_brief_path.exists():
            print(f"error: topic brief not found: {topic_brief_path}", file=sys.stderr)
            return 2

        result = generate_youtube_dry_run(
            run_dir=run_dir,
            topic_brief_path=topic_brief_path,
            sources_path=sources_path,
            video_file=args.video_file,
            thumbnail_file=args.thumbnail_file,
            caption_file=args.caption_file,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: failed to generate YouTube SEO dry-run: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
