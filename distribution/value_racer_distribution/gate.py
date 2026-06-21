"""Distribution gates, one per content_type. Both read their ScenePlan/EmpireScenePlan JSON
document as a plain dict — never import value_racer_brain classes, per the project's module
boundary rule (modules exchange JSON contracts, not internal types).

## imperium — "Strengeres Gate" (see project plan and EMPIRE_SCENE_PLAN.md's "Bewusste Grenze
der Autonomie"). Three independent reasons force `pending_review`, any one is enough:

1. `qa.hard_fail` — structural QA failed (missing fields, too few sourced brands/facts/rows).
2. `qa.sources_verified == false` — covers both a never-verified episode AND a stale one, since
   qa.py already folds `verify_interval_days` staleness into `sources_verified` itself.
3. First contact — no prior post exists for this `topic.topic_id`. Even a fully green episode
   about a company never posted before always needs a human look once, by design.

Periodic re-verification isn't a fourth, separate check here for the same reason as (2): once an
episode goes stale, `sources_verified` flips to false on its own, which already routes it back
into manual review without any distribution-side staleness logic.

## chart_race — "Hybrid-Freigabe-Gate" (less strict: live market data, no research risk, so no
first-contact rule). Two independent reasons force `pending_review`:

1. `qa.hard_fail` — structural QA failed (event overlap, asset count, time-map endpoint, ...).
2. The `advisory_wording` entry in `qa.results` is missing or `passed == false` — the title reads
   like investment advice (see value_racer_brain/advisory.py). The project plan describes this
   check as living on a `PostingPackage` produced by seo-engine; since seo-engine doesn't exist
   yet and the Brain already runs the same check and embeds its result directly in
   `ScenePlan.qa.results`, the gate reads it from there for now — swap the source once seo-engine
   ships its own `PostingPackage` contract.
"""

from __future__ import annotations

from .history import PostHistory
from .models import GateDecision


def evaluate_imperium_gate(plan: dict, history: PostHistory) -> GateDecision:
    qa = plan["qa"]
    topic_id = plan["topic"]["topic_id"]

    reasons: list[str] = []
    if qa["hard_fail"]:
        reasons.append("qa_hard_fail")
    if not qa["sources_verified"]:
        reasons.append("sources_not_verified")
    if not history.has_posted(topic_id):
        reasons.append("first_contact_requires_manual_review")

    status = "pending_review" if reasons else "auto_post"
    return GateDecision(status=status, reasons=reasons)


def evaluate_chart_race_gate(plan: dict) -> GateDecision:
    qa = plan["qa"]

    reasons: list[str] = []
    if qa["hard_fail"]:
        reasons.append("qa_hard_fail")

    advisory = next((r for r in qa["results"] if r["check"] == "advisory_wording"), None)
    if advisory is None or not advisory["passed"]:
        reasons.append("advisory_wording_flagged")

    status = "pending_review" if reasons else "auto_post"
    return GateDecision(status=status, reasons=reasons)
