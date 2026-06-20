"""ScenePlan — the sole interface between Brain and Renderer.

Field names and nesting mirror content-engine/SCENE_PLAN.md exactly (read-only
contract). Pydantic models so to_json()/from_json() round-trip and validate
field types without us hand-rolling JSON schema checks.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

SCHEMA_VERSION = 1


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Topic(_Base):
    assets: List[str]
    period_days: int
    locale: str = "de"


class Phase(_Base):
    start_frame: int
    end_frame: int


class Phases(_Base):
    intro: Phase
    race: Phase
    final_hold: Phase
    endscreen: Phase


class Duration(_Base):
    total_frames: int
    total_duration_sec: float
    phases: Phases


class DataSeries(_Base):
    ticker: str
    label: str
    color: str
    dates: List[str]
    # Optional: a ticker with a later IPO can still have leading NaNs inside the
    # common df index in rare reindex edge cases; renderer should treat null as "no data yet".
    values: List[Optional[float]]


class CameraKeyframeOut(_Base):
    frame: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float


class Camera(_Base):
    policy: str  # "stock_value" | "percent" | "high_volatility"
    keyframes: List[CameraKeyframeOut]


class TimeMapControlPoint(_Base):
    frame: int
    data_index: float


class TimeMap(_Base):
    enabled: bool
    control_points: List[TimeMapControlPoint]


class EventOut(_Base):
    frame_start: int
    frame_end: int
    ticker: Optional[str] = None
    type: str
    label: str  # <=42 chars per contract
    style_ref: str


class ThemeColors(_Base):
    bg: dict
    text: dict
    accent: dict


class Theme(_Base):
    id: str
    colors: ThemeColors
    font_family: str
    glow_mode: str  # "full" | "subtle" | "reduced" | "minimal"
    event_styles: dict


class HookVariant(_Base):
    id: str


class FinalValue(_Base):
    ticker: str
    value: float
    gain_pct: float


class Endscreen(_Base):
    final_values: List[FinalValue]
    thumbnail_source_frame: int


class QAResultEntry(_Base):
    check: str
    passed: bool
    detail: str = ""


class QA(_Base):
    hard_fail: bool
    results: List[QAResultEntry]


class ScenePlan(_Base):
    schema_version: int = SCHEMA_VERSION
    video_id: str
    topic: Topic
    fps: int
    duration: Duration
    data_series: List[DataSeries]
    camera: Camera
    time_map: TimeMap
    events: List[EventOut]
    theme: Theme
    hook_variant: HookVariant
    endscreen: Endscreen
    qa: QA

    def to_json(self, indent: int = 2) -> str:
        return self.model_dump_json(indent=indent)

    @classmethod
    def from_json(cls, raw: str) -> "ScenePlan":
        return cls.model_validate_json(raw)
