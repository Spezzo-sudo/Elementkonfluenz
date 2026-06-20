"""CLI entry point: python -m elementkonfluenz_brain.cli --tickers ... --days N --out path.json"""

from __future__ import annotations

import argparse
import logging
import sys

from .builder import build_scene_plan


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="elementkonfluenz_brain.cli", description="Build a ScenePlan JSON document.")
    parser.add_argument("--tickers", required=True, help="Comma-separated tickers, e.g. BTC-USD,^GSPC")
    parser.add_argument("--days", type=int, default=1825, help="Lookback period in days")
    parser.add_argument("--out", required=True, help="Output path for scene_plan.json")
    parser.add_argument("--locale", default="de")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--investment", type=float, default=1000.0)
    parser.add_argument("--mode", default="evergreen", choices=["evergreen", "news"])
    parser.add_argument("--hook-title", default="", help="Video title; checked for advisory-wording red flags")
    parser.add_argument("--theme-id", default="default_dark")
    parser.add_argument("--hook-variant-id", default="default")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
    if len(tickers) < 2:
        print("error: need at least 2 tickers", file=sys.stderr)
        return 2

    topic_brief = {
        "assets": tickers,
        "period_days": args.days,
        "locale": args.locale,
        "fps": args.fps,
        "investment": args.investment,
        "mode": args.mode,
        "hook_title": args.hook_title,
        "events": [],
    }

    try:
        plan = build_scene_plan(topic_brief, theme={}, hook_variant={"id": args.hook_variant_id})
    except Exception as exc:  # noqa: BLE001 - surface a clean CLI error rather than a traceback
        print(f"error: failed to build scene plan: {exc}", file=sys.stderr)
        return 1

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(plan.to_json())

    print(f"wrote {args.out} (video_id={plan.video_id}, hard_fail={plan.qa.hard_fail})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
