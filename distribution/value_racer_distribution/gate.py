"""Distribution gate for the imperium vertical ("Strengeres Gate (imperium)", see project plan
and content-engine/EMPIRE_SCENE_PLAN.md's "Bewusste Grenze der Autonomie").

Reads the EmpireScenePlan JSON document as a plain dict — never imports value_racer_brain
classes, per the project's module boundary rule (modules exchange JSON contracts, not internal
types). Three independent reasons force `pending_review`, any one of them is enough:

1. `qa.hard_fail` — structural QA failed (missing fields, too few sourced brands/facts/rows).
2. `qa.sources_verified == false` — covers both a never-verified episode AND a stale one, since
   qa.py already folds `verify_interval_days` staleness into `sources_verified` itself.
3. First contact — no prior post exists for this `topic.topic_id`. Even a fully green episode
   about a company never posted before always needs a human look once, by design.

Periodic re-verification isn't a fourth, separate check here for the same reason as (2): once an
episode goes stale, `sources_verified` flips to false on its own, which already routes it back
into manual review without any distribution-side staleness logic.
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
