"""EmpireScenePlan — the sole interface between Brain (imperium) and Renderer (ImperiumComposition).

Field names mirror content-engine/EMPIRE_SCENE_PLAN.md (read-only contract). Deliberately not
reusing scene_plan.ScenePlan's shape — imperium has no time-series camera, it has a fixed
card/stamp/bar-chart phase timeline instead. See content-engine/brain/value_racer_brain/scene_plan.py
for the sibling chart_race contract.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict

SCHEMA_VERSION = 1


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Topic(_Base):
    topic_id: str
    company_name: str
    ticker: str
    sector: str
    region: str


class Phase(_Base):
    start_frame: int
    end_frame: int


class Phases(_Base):
    hook: Phase
    register_cards: Phase
    beat: Phase
    stamp: Phase
    facts: Phase
    scale: Phase
    endcard: Phase


class Duration(_Base):
    total_frames: int
    total_duration_sec: float
    phases: Phases


class Owner(_Base):
    display_name: str
    legal_name: str
    hq_city: str
    founded_year: int


class BrandCard(_Base):
    name: str
    category: str
    year: int
    color: str
    text_color: str


class FactCard(_Base):
    label: str
    display_value: str
    unit: str
    year: int
    description: str


class ScaleComparisonRow(_Base):
    label: str
    value: float
    hero: bool


class ScaleComparisonOut(_Base):
    headline: str
    unit: str
    rows: List[ScaleComparisonRow]


class Endcard(_Base):
    ticker_label: str
    stock_from: float
    stock_to: float
    gain_pct: float
    disclaimer: str


class Theme(_Base):
    id: str
    accent_color: str
    stamp_color: str


class QAResultEntry(_Base):
    check: str
    passed: bool
    detail: str = ""


class QA(_Base):
    hard_fail: bool
    sources_verified: bool
    results: List[QAResultEntry]


class EmpireScenePlan(_Base):
    schema_version: int = SCHEMA_VERSION
    video_id: str
    topic: Topic
    fps: int
    duration: Duration
    owner: Owner
    hook_lines: List[str]
    beat_line: str
    brands: List[BrandCard]
    facts: List[FactCard]
    scale_comparison: ScaleComparisonOut
    endcard: Endcard
    theme: Theme
    qa: QA

    def to_json(self, indent: int = 2) -> str:
        return self.model_dump_json(indent=indent)

    @classmethod
    def from_json(cls, raw: str) -> "EmpireScenePlan":
        return cls.model_validate_json(raw)
