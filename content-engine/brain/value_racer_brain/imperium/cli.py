"""CLI entry point: python -m value_racer_brain.imperium.cli build --data path.yaml --out path.json
or: python -m value_racer_brain.imperium.cli research-status [--data-dir path]
"""

from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from . import qa as qa_mod
from .builder import build_empire_scene_plan
from .research import CompanyResearch

DEFAULT_DATA_DIR = Path(__file__).parent / "data"


def _load_research(path: Path) -> CompanyResearch:
    return CompanyResearch.from_yaml(path.read_text(encoding="utf-8"))


def _cmd_build(args: argparse.Namespace) -> int:
    research = _load_research(Path(args.data))
    plan = build_empire_scene_plan(research, fps=args.fps, period_days=args.days, investment=args.investment)
    Path(args.out).write_text(plan.to_json(), encoding="utf-8")
    print(
        f"wrote {args.out} (video_id={plan.video_id}, hard_fail={plan.qa.hard_fail}, "
        f"sources_verified={plan.qa.sources_verified})"
    )
    return 0


def _cmd_research_status(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir)
    today = date.today()
    rows = []
    for f in sorted(data_dir.glob("*.yaml")):
        research = _load_research(f)
        report = qa_mod.run_qa(research, today=today)
        if report.sources_verified:
            verification = "verified"
        elif report.is_stale:
            verification = "STALE"
        else:
            verification = "UNVERIFIED"
        rows.append((f.name, research.owner.display_name, verification, "VIOLATION" if report.hard_fail else "ok"))

    if not rows:
        print(f"no episodes found in {data_dir}")
        return 0

    name_width = max(len(r[1]) for r in rows)
    for fname, company, verification, structural in rows:
        print(f"{fname:30s} {company:{name_width}s}  verification={verification:10s} structural_qa={structural}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="value_racer_brain.imperium.cli", description="Build/inspect Imperium episodes.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Build an EmpireScenePlan JSON document from a research YAML.")
    p_build.add_argument("--data", required=True, help="Path to a research YAML (see research.py)")
    p_build.add_argument("--out", required=True, help="Output path for empire_scene_plan.json")
    p_build.add_argument("--fps", type=int, default=30)
    p_build.add_argument("--days", type=int, default=3650, help="Lookback period for endcard stock performance")
    p_build.add_argument("--investment", type=float, default=1000.0)
    p_build.set_defaults(func=_cmd_build)

    p_status = sub.add_parser(
        "research-status", help="List all research YAMLs with verification/staleness/structural-QA status."
    )
    p_status.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    p_status.set_defaults(func=_cmd_research_status)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
