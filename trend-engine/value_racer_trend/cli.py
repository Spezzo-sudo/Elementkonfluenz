"""CLI: pick the next topic, or simulate a sequence of picks to verify anti-repetition."""
from __future__ import annotations

import argparse
import json

from .scorer import MAX_CONSECUTIVE, pick_next_topic
from .store import HistoryStore


def _max_consecutive_runs(sequence: list[str]) -> dict[str, int]:
    best = {ct: 0 for ct in MAX_CONSECUTIVE}
    if not sequence:
        return best
    cur = sequence[0]
    run = 1
    best[cur] = 1
    for prev, ct in zip(sequence, sequence[1:]):
        run = run + 1 if ct == prev else 1
        best[ct] = max(best[ct], run)
    return best


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db",
        default=None,
        help="SQLite history db path (default: trend_history.sqlite3 next to the package)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="pick a topic without persisting it to history",
    )
    parser.add_argument(
        "--simulate",
        type=int,
        default=0,
        help="run N picks against an isolated in-memory history, print the content_type "
        "sequence and the longest consecutive same-type run (must stay <= 2)",
    )
    args = parser.parse_args()

    if args.simulate:
        store = HistoryStore(db_path=":memory:")
        sequence = [pick_next_topic(store).content_type for _ in range(args.simulate)]
        print(" ".join(sequence))
        runs = _max_consecutive_runs(sequence)
        for content_type, cap in MAX_CONSECUTIVE.items():
            status = "ok" if runs[content_type] <= cap else "VIOLATION"
            print(f"max_consecutive[{content_type}]={runs[content_type]} (cap={cap}, {status})")
        return

    store = HistoryStore(db_path=args.db) if args.db else HistoryStore()
    brief = pick_next_topic(store, persist=not args.dry_run)
    print(json.dumps(brief.model_dump(mode="json"), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
