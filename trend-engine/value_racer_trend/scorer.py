"""Cross-vertical scorer.

Picks content_type first (weighted, with a hard anti-repetition rule), then a
concrete topic within that vertical (cooldown filter + category/sector rotation).

trend_score is currently always 0.0 -- Google Trends/GDELT/RSS signals are not
wired up yet (see trend-engine/README.md). Once they exist, they replace the
recency-based tie-breaker below without changing the TopicBrief contract.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Optional

from .catalog_chart_race import CATALOG as CHART_RACE_CATALOG
from .catalog_imperium import CATALOG as IMPERIUM_CATALOG
from .models import ChartRaceTopic, ImperiumTopic, TopicBrief
from .store import HistoryStore

DEFAULT_WEIGHTS = {"chart_race": 4, "imperium": 1}
# Asymmetric on purpose: a symmetric cap (e.g. "max 2 in a row" for both types)
# mathematically limits the achievable long-run ratio to 2:1, which contradicts a
# 4:1 weight target (confirmed empirically: AABAAB... tops out at 2:1, never 4:1).
# The actual intent is asymmetric anyway -- chart_race runs are cheap (live data,
# no research), imperium episodes are research-heavy, so back-to-back imperium
# picks are the thing worth hard-blocking, not chart_race streaks.
MAX_CONSECUTIVE = {"chart_race": 4, "imperium": 1}
TOPIC_COOLDOWN_DAYS = 21


def _days_since(dt: Optional[datetime]) -> float:
    if dt is None:
        return float("inf")
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).total_seconds() / 86400.0


def _current_run(store: HistoryStore, caps: dict[str, int]) -> tuple[Optional[str], int]:
    recent = store.recent_content_types(limit=max(caps.values()))
    if not recent:
        return None, 0
    last_type = recent[0]
    run = 0
    for entry in recent:
        if entry == last_type:
            run += 1
        else:
            break
    return last_type, run


def choose_content_type(
    store: HistoryStore,
    weights: dict[str, int] = DEFAULT_WEIGHTS,
    caps: dict[str, int] = MAX_CONSECUTIVE,
) -> str:
    """Deficit-based scheduler: picks whichever content_type is furthest below its
    configured target share, so the long-run ratio converges to `weights` instead of
    drifting (a hard cap combined with pure random sampling skews the realized ratio
    toward the minority type -- confirmed empirically before this was written).
    The per-type consecutive-run cap is enforced as a hard safety net on top.
    """
    last_type, run = _current_run(store, caps)
    blocked = last_type if last_type is not None and run >= caps.get(last_type, float("inf")) else None
    candidates = [c for c in weights if c != blocked]
    if len(candidates) == 1:
        return candidates[0]

    counts = store.content_type_counts()
    total = sum(counts.get(c, 0) for c in weights)
    if total == 0:
        pool: list[str] = []
        for c in candidates:
            pool += [c] * weights[c]
        return random.choice(pool)

    total_weight = sum(weights.values())

    def deficit(c: str) -> float:
        target_share = weights[c] / total_weight
        actual_share = counts.get(c, 0) / total
        return target_share - actual_share

    return max(candidates, key=deficit)


def _pick_topic(store: HistoryStore, content_type: str, catalog):
    eligible = []
    for topic in catalog:
        tag = topic.category if content_type == "chart_race" else topic.sector
        topic_age = _days_since(store.topic_last_used(topic.topic_id))
        if topic_age < TOPIC_COOLDOWN_DAYS:
            continue
        tag_age = _days_since(store.tag_last_used(content_type, tag))
        eligible.append((tag_age, topic))
    if not eligible:
        # every topic is within cooldown -- fall back to least-recently-used overall
        eligible = [
            (_days_since(store.topic_last_used(t.topic_id)), t) for t in catalog
        ]
    eligible.sort(key=lambda pair: pair[0], reverse=True)
    return eligible[0][1]


def pick_next_topic(
    store: HistoryStore,
    weights: dict[str, int] = DEFAULT_WEIGHTS,
    persist: bool = True,
) -> TopicBrief:
    content_type = choose_content_type(store, weights)
    now = datetime.now(timezone.utc)

    if content_type == "chart_race":
        topic: ChartRaceTopic = _pick_topic(store, "chart_race", CHART_RACE_CATALOG)
        brief = TopicBrief(
            content_type="chart_race",
            selected_at=now,
            trend_score=0.0,
            reason=f"category-rotation pick, category={topic.category}",
            chart_race=topic,
        )
        if persist:
            store.record("chart_race", topic.topic_id, tag=topic.category, when=now)
    else:
        topic: ImperiumTopic = _pick_topic(store, "imperium", IMPERIUM_CATALOG)
        brief = TopicBrief(
            content_type="imperium",
            selected_at=now,
            trend_score=0.0,
            reason=f"sector-rotation pick, sector={topic.sector}",
            imperium=topic,
        )
        if persist:
            store.record("imperium", topic.topic_id, tag=topic.sector, when=now)

    return brief
