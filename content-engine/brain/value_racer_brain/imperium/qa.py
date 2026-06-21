"""qa.py — structural QA gate for CompanyResearch episodes.

Pure validation, no rendering. Mirrors the chart_race Brain's QA philosophy:
deterministic checks with an explicit pass/fail + detail string each, no implicit
magic. The rule that matters most for this vertical is `sources_verified` —
distribution treats it as a hard gate on top of these structural checks (a
first-contact episode or a stale one always needs manual review regardless of
how clean this report is, see trend-engine/README.md and the project plan).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from .research import CompanyResearch

MIN_BRANDS = 6
MAX_BRANDS = 12
MIN_FACTS = 3
MIN_SCALE_ROWS = 3  # hero + at least 2 comparison companies


@dataclass
class QAResult:
    check: str
    passed: bool
    detail: str = ""


@dataclass
class QAReport:
    hard_fail: bool
    sources_verified: bool
    is_stale: bool
    results: List[QAResult] = field(default_factory=list)


def _all_sourced(items) -> bool:
    return all(bool(getattr(item, "source_url", "")) for item in items)


def run_qa(research: CompanyResearch, today: Optional[date] = None) -> QAReport:
    today = today or date.today()
    results: List[QAResult] = []

    results.append(QAResult(
        check="brand_count",
        passed=MIN_BRANDS <= len(research.brands) <= MAX_BRANDS,
        detail=f"{len(research.brands)} brands (need {MIN_BRANDS}-{MAX_BRANDS})",
    ))
    results.append(QAResult(
        check="brands_sourced",
        passed=_all_sourced(research.brands),
        detail="ok" if _all_sourced(research.brands) else "brand without source_url",
    ))
    results.append(QAResult(
        check="fact_count",
        passed=len(research.facts) >= MIN_FACTS,
        detail=f"{len(research.facts)} facts (need >={MIN_FACTS})",
    ))
    results.append(QAResult(
        check="facts_sourced",
        passed=_all_sourced(research.facts),
        detail="ok" if _all_sourced(research.facts) else "fact without source_url",
    ))
    results.append(QAResult(
        check="scale_comparison_rows",
        passed=len(research.scale_comparison.rows) >= MIN_SCALE_ROWS,
        detail=f"{len(research.scale_comparison.rows)} rows (need >={MIN_SCALE_ROWS})",
    ))
    results.append(QAResult(
        check="scale_comparison_sourced",
        passed=_all_sourced(research.scale_comparison.rows),
        detail="ok" if _all_sourced(research.scale_comparison.rows) else "comparison row without source_url",
    ))

    is_stale = bool(
        research.verified and research.verified_at is not None
        and (today - research.verified_at).days > research.verify_interval_days
    )
    results.append(QAResult(
        check="verification_fresh",
        passed=not is_stale,
        detail="ok" if not is_stale else f"verified_at older than {research.verify_interval_days} days",
    ))

    # Staleness is a distribution-gate concern (re-verification), not a reason to
    # block rendering outright — it only suppresses sources_verified below.
    hard_fail = any(not r.passed for r in results if r.check != "verification_fresh")

    return QAReport(
        hard_fail=hard_fail,
        sources_verified=research.verified and not is_stale,
        is_stale=is_stale,
        results=results,
    )
