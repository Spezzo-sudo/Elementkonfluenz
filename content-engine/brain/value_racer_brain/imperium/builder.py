"""build_empire_scene_plan — wires CompanyResearch (+ one live stock lookup) into an EmpireScenePlan.

Brain's single entry point for the imperium vertical (mirrors content-engine/brain's chart_race
builder.py in spirit: one function, no class). The endcard stock performance is the *only* live
data point in this vertical — fetched via yfinance same as chart_race — because it's the one
fact about a real company that an API actually answers reliably. Brands, facts and the scale
comparison come exclusively from the curated, sourced `research` input and are never auto-fetched;
see research.py for why.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import yfinance as yf

from . import qa as qa_mod
from .research import CompanyResearch
from .scene_plan import (
    BrandCard,
    Duration,
    Endcard,
    EmpireScenePlan,
    FactCard,
    Owner,
    Phase,
    Phases,
    QA,
    QAResultEntry,
    ScaleComparisonOut,
    ScaleComparisonRow,
    Theme,
    Topic,
)

DEFAULT_THEME = {"id": "imperium_dark", "accent_color": "#C0392B", "stamp_color": "#8B0000"}

# Fixed phase timeline (seconds), mirroring the HTML prototype's
# hook/register/beat/stamp/facts/scale/endcard structure.
_PHASE_SECONDS = {
    "hook": 2.0, "register_cards": 4.0, "beat": 1.5, "stamp": 1.5,
    "facts": 5.0, "scale": 4.0, "endcard": 3.0,
}


def _download_stock_endcard(ticker: str, period_days: int, investment: float) -> Tuple[float, float]:
    """Single-ticker $investment-since-period_days-ago performance.

    Deliberately not reusing value_racer_brain.data.download_data_sync, which hard-requires
    >=2 tickers for a comparison race — imperium only ever needs one.
    """
    end = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    start = end - pd.Timedelta(days=period_days)
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if df.empty:
        return investment, investment
    prices = df["Close"].iloc[:, 0] if isinstance(df.columns, pd.MultiIndex) else df["Close"]
    prices = prices.dropna()
    if len(prices) < 2:
        return investment, investment
    final_value = investment * (prices.iloc[-1] / prices.iloc[0])
    return investment, round(float(final_value), 2)


def _format_value(value: float, unit: str) -> str:
    """German thousands/decimal formatting, e.g. 271000 -> '271.000', 91.4 -> '91,4'."""
    if unit.startswith("Mrd") or unit.startswith("Mio"):
        return f"{value:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{value:,.0f}".replace(",", ".")


def _build_phases(fps: int) -> Tuple[Phases, int]:
    cursor = 0
    phase_objs: Dict[str, Phase] = {}
    for key, seconds in _PHASE_SECONDS.items():
        start = cursor
        cursor += round(seconds * fps)
        phase_objs[key] = Phase(start_frame=start, end_frame=cursor)
    return Phases(**phase_objs), cursor


def build_empire_scene_plan(
    research: CompanyResearch,
    fps: int = 30,
    period_days: int = 3650,
    investment: float = 1000.0,
    theme: Optional[Dict[str, Any]] = None,
) -> EmpireScenePlan:
    report = qa_mod.run_qa(research)

    phases, total_frames = _build_phases(fps)

    brands_sorted = sorted(research.brands, key=lambda b: b.surprise_factor)[:12]
    brand_cards = [
        BrandCard(name=b.name, category=b.category, year=b.acquired_year, color=b.color_primary, text_color=b.color_text)
        for b in brands_sorted
    ]

    fact_cards = [
        FactCard(
            label=f.label, display_value=_format_value(f.value, f.unit), unit=f.unit,
            year=f.as_of_year, description=f.description,
        )
        for f in research.facts[:3]
    ]

    scale_rows = [
        ScaleComparisonRow(label=r.label, value=r.value, hero=(i == 0))
        for i, r in enumerate(research.scale_comparison.rows)
    ]

    stock_from, stock_to = _download_stock_endcard(research.owner.ticker, period_days, investment)
    gain_pct = round((stock_to / stock_from - 1) * 100, 2) if stock_from else 0.0

    theme_dict = theme or DEFAULT_THEME
    qa_results = [QAResultEntry(check=r.check, passed=r.passed, detail=r.detail) for r in report.results]

    return EmpireScenePlan(
        video_id=str(uuid.uuid4()),
        topic=Topic(
            topic_id=research.topic_id, company_name=research.owner.display_name,
            ticker=research.owner.ticker, sector=research.sector, region=research.region,
        ),
        fps=fps,
        duration=Duration(total_frames=total_frames, total_duration_sec=round(total_frames / fps, 3), phases=phases),
        owner=Owner(
            display_name=research.owner.display_name, legal_name=research.owner.legal_name,
            hq_city=research.owner.hq_city, founded_year=research.owner.founded_year,
        ),
        hook_lines=["WEM GEHÖRT", "DAS ALLES?"],
        beat_line="ALLE SPUREN FÜHREN ZU EINEM NAMEN",
        brands=brand_cards,
        facts=fact_cards,
        scale_comparison=ScaleComparisonOut(
            headline=research.scale_comparison.headline, unit=research.scale_comparison.unit, rows=scale_rows,
        ),
        endcard=Endcard(
            ticker_label=f"AKTIE · {research.owner.ticker} · {period_days // 365} JAHRE",
            stock_from=stock_from, stock_to=stock_to, gain_pct=gain_pct,
            disclaimer="Keine Anlageberatung · Vergangenheit ungleich Zukunft",
        ),
        theme=Theme(**theme_dict),
        qa=QA(hard_fail=report.hard_fail, sources_verified=report.sources_verified, results=qa_results),
    )
