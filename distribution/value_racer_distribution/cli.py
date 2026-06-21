"""CLI entry point: python -m value_racer_distribution.cli gate --plan empire_scene_plan.json
or: python -m value_racer_distribution.cli record-post --plan empire_scene_plan.json

`record-post` stands in for the real posting integration (YouTube Data API etc., still Phase 6
in the project plan) — it lets the imperium gate's first-contact check be exercised and
verified end-to-end today, without a live posting pipeline behind it yet.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .gate import evaluate_imperium_gate
from .history import DEFAULT_DB_PATH, PostHistory


def _load_plan(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _cmd_gate(args: argparse.Namespace) -> int:
    plan = _load_plan(Path(args.plan))
    history = PostHistory(args.db)
    decision = evaluate_imperium_gate(plan, history)
    history.close()
    reasons = ", ".join(decision.reasons) if decision.reasons else "-"
    print(f"video_id={plan.get('video_id')} status={decision.status} reasons={reasons}")
    return 0


def _cmd_record_post(args: argparse.Namespace) -> int:
    plan = _load_plan(Path(args.plan))
    history = PostHistory(args.db)
    history.record_post(
        content_type="imperium",
        topic_id=plan["topic"]["topic_id"],
        video_id=plan["video_id"],
    )
    history.close()
    print(f"recorded post: topic_id={plan['topic']['topic_id']} video_id={plan['video_id']}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="value_racer_distribution.cli", description="Distribution gate for produced episodes."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_gate = sub.add_parser("gate", help="Evaluate the imperium distribution gate for an EmpireScenePlan JSON.")
    p_gate.add_argument("--plan", required=True, help="Path to an EmpireScenePlan JSON document.")
    p_gate.add_argument("--db", default=str(DEFAULT_DB_PATH))
    p_gate.set_defaults(func=_cmd_gate)

    p_record = sub.add_parser(
        "record-post", help="Mark a topic_id as posted, clearing first-contact for future episodes."
    )
    p_record.add_argument("--plan", required=True)
    p_record.add_argument("--db", default=str(DEFAULT_DB_PATH))
    p_record.set_defaults(func=_cmd_record_post)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
