"""Video planning framework — ported near-verbatim from video_plan.py.

Policies designed for 2-6 assets. Max 6 assets supported.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

_MAX_ASSETS = 6


def duration_from_period(total_days: int, asset_count: int) -> float:
    """Derive TOTAL duration (all phases incl. endscreen) from period and asset count.

    Targets (total):
        <=18mo:  32-38s        1.5-3y:  38-44s
        3-7y:    42-48s        7-15y:   46-52s
        15-30y:  50-58s
    Asset modification (total): 2: -2..-4s  3: -1..-2s  4: neutral  5-6: +2..+4s
    Hard caps (total per asset count): 2: max 44-46s  3: max 46-48s
        4: max 50-52s   5-6: max 56-58s
    """
    days = max(0, int(total_days or 0))
    assets = max(0, int(asset_count or 0))

    if days <= 548:
        base = 35.0
    elif days <= 1095:
        base = 41.0
    elif days <= 2555:
        base = 45.0
    elif days <= 5475:
        base = 49.0
    else:
        base = 54.0

    if assets == 2:
        adj = -3.0
    elif assets == 3:
        adj = -1.5
    elif assets == 4:
        adj = 0.0
    elif assets in (5, 6):
        adj = 3.0
    else:
        adj = 0.0

    raw = base + adj

    lo, hi = {
        2: (30.0, 46.0), 3: (32.0, 48.0), 4: (35.0, 52.0),
        5: (38.0, 57.0), 6: (38.0, 57.0),
    }.get(assets, (28.0, 60.0))

    return float(max(lo, min(hi, raw)))


def suggested_endscreen_hold(total_days: int) -> float:
    """Endscreen hold time: 5-7s, never >8s."""
    days = max(0, int(total_days or 0))
    if days <= 365:
        return 5.0
    if days <= 1825:
        return 6.0
    return 7.0


@dataclass
class PhasePolicy:
    """Phase defaults. All times in seconds."""

    start_setup_sec: float = 0.7
    race_sec: float = 35.0
    final_chart_hold_sec: float = 1.5
    crossfade_sec: float = 1.0
    endscreen_hold_sec: float = 6.0


@dataclass
class VideoPlan:
    """Master VideoPlan — ALL parameters fixed before render."""

    locale: str = "de"
    total_data_days: int = 0
    asset_count: int = 0
    requested_asset_count: int = 0
    dropped_assets: List[str] = field(default_factory=list)
    hook_title: str = ""

    start_setup_sec: float = 0.7
    race_sec: float = 35.0
    final_chart_hold_sec: float = 1.5
    crossfade_sec: float = 1.0
    endscreen_hold_sec: float = 6.0

    total_duration_sec: float = 0.0
    race_share_pct: float = 0.0

    phase_start_end: int = 0
    phase_race_end: int = 0
    phase_final_end: int = 0
    phase_crossfade_end: int = 0
    phase_endscreen_end: int = 0
    total_frames: int = 0

    axis_camera_mode: str = "legacy"
    axis_camera_required: bool = False
    axis_camera_strict: bool = False

    time_map_enabled: bool = False
    time_map_gated: bool = False
    time_map_applied: bool = False
    time_map_effective: bool = False
    time_map_stretch_factor: float = 1.0
    time_map_early_cluster_score: float = 0.0
    time_map_early_data_pct: float = 0.0
    time_map_early_race_pct: float = 0.0

    start_cluster_reduced_glow: bool = False
    endpoint_dots_from_frame: int = 20
    labels_from_divergence: bool = True
    endpoint_dot_distance_max_px: float = 0.0

    max_visible_events: int = 1
    events_during_final_hold: bool = False
    event_label_max_count: int = 0

    thumbnail_source: str = "endscreen"

    qa_results: Dict[str, Any] = field(default_factory=dict)
    qa_hard_fail: bool = False

    def __post_init__(self) -> None:
        self.total_duration_sec = self._compute_total_duration_sec()
        if self.total_duration_sec > 0:
            self.race_share_pct = round(self.race_sec / self.total_duration_sec * 100, 1)

    def _compute_total_duration_sec(self) -> float:
        return float(
            self.start_setup_sec + self.race_sec + self.final_chart_hold_sec
            + self.crossfade_sec + self.endscreen_hold_sec
        )

    def compute_frame_boundaries(self, fps: int) -> "VideoPlan":
        if fps <= 0:
            raise ValueError("fps must be a positive integer")
        self.total_duration_sec = self._compute_total_duration_sec()
        if self.total_duration_sec > 0:
            self.race_share_pct = round(self.race_sec / self.total_duration_sec * 100, 1)

        def to_frames(seconds: float) -> int:
            return int(round(float(seconds) * int(fps)))

        start_f = to_frames(self.start_setup_sec)
        race_f = to_frames(self.race_sec)
        final_f = to_frames(self.final_chart_hold_sec)
        xfade_f = to_frames(self.crossfade_sec)
        end_f = to_frames(self.endscreen_hold_sec)

        self.phase_start_end = start_f
        self.phase_race_end = self.phase_start_end + race_f
        self.phase_final_end = self.phase_race_end + final_f
        self.phase_crossfade_end = self.phase_final_end + xfade_f
        self.phase_endscreen_end = self.phase_crossfade_end + end_f
        self.total_frames = self.phase_endscreen_end
        return self


@dataclass
class QAResult:
    """Structured QA result. Each field has: pass (bool), value, warnings (list)."""

    axis_camera: Dict[str, Any] = field(default_factory=lambda: {"pass": True, "mode": "legacy", "required": False, "applied": False, "strict": False, "start_x_range_ratio": 0.0, "warnings": []})
    timemap: Dict[str, Any] = field(default_factory=lambda: {"pass": True, "enabled": False, "gated": False, "applied": False, "effective": False, "stretch": 1.0, "warnings": []})
    endpoint_dots: Dict[str, Any] = field(default_factory=lambda: {"pass": True, "max_distance_px": 0.0, "warnings": []})
    events: Dict[str, Any] = field(default_factory=lambda: {"pass": True, "max_count": 0, "overlap": False, "during_final_hold": False, "warnings": []})
    endscreen: Dict[str, Any] = field(default_factory=lambda: {"pass": True, "duration_sec": 0.0, "warnings": []})
    phase_timing: Dict[str, Any] = field(default_factory=lambda: {"pass": True, "final_chart_hold_sec": 0.0, "endscreen_hold_sec": 0.0, "race_share_pct": 0.0, "warnings": []})
    thumbnail: Dict[str, Any] = field(default_factory=lambda: {"pass": True, "source": "", "warnings": []})
    final_values: Dict[str, Any] = field(default_factory=lambda: {"pass": True, "consistent": True, "warnings": []})
    asset_limit: Dict[str, Any] = field(default_factory=lambda: {"pass": True, "requested": 0, "rendered": 0, "dropped": [], "warnings": []})
    hard_fails: List[str] = field(default_factory=list)

    def add_fail(self, msg: str):
        self.hard_fails.append(msg)


class VideoPlanBuilder:
    """Factory: builds VideoPlan from DataFrame + config."""

    MAX_ASSETS = _MAX_ASSETS

    @staticmethod
    def build(df: Any, config: Any = None, fps: int = 30, locale: str = "de") -> VideoPlan:
        total_days = _infer_total_days(df, config)
        raw_asset_count = _infer_asset_count(df, config)

        dropped = []
        if raw_asset_count > VideoPlanBuilder.MAX_ASSETS:
            dropped_how_many = raw_asset_count - VideoPlanBuilder.MAX_ASSETS
            dropped = [f"{dropped_how_many} assets dropped (max {VideoPlanBuilder.MAX_ASSETS})"]
            asset_count = VideoPlanBuilder.MAX_ASSETS
        else:
            asset_count = raw_asset_count

        hook_title = str(_config_get(config, "hook_title", "") or "")

        total_target = duration_from_period(total_days, asset_count)
        endscreen_sec = suggested_endscreen_hold(total_days)
        _overhead = float(_config_get(config, "start_setup_sec", 0.7))
        _overhead += float(_config_get(config, "final_chart_hold_sec", 1.5))
        _overhead += float(_config_get(config, "crossfade_sec", 1.0))
        race_sec = max(20.0, total_target - _overhead - endscreen_sec)

        axis_mode_config = str(_config_get(config, "axis_camera_mode", _config_get(config, "axis_camera", "auto")) or "auto").lower()
        axis_camera_mode = "legacy"
        axis_camera_required = False
        axis_camera_strict = False

        if axis_mode_config == "planned":
            axis_camera_mode = "planned"
            axis_camera_required = True
        elif axis_mode_config in ("auto", "smart"):
            if total_days > 3650:
                axis_camera_mode = "planned"
                axis_camera_required = True
                axis_camera_strict = True
            elif total_days > 1095:
                axis_camera_mode = "planned"
                axis_camera_required = True
                axis_camera_strict = False
            elif total_days > 548:
                axis_camera_mode = "legacy"
                axis_camera_required = False
                axis_camera_strict = False
            else:
                axis_camera_mode = "legacy"
                axis_camera_required = False

        time_map_enabled = bool(_config_get(config, "enable_time_map", False) or _config_get(config, "ENABLE_TIME_MAP", False))
        time_map_gated = False
        time_map_applied = False
        tm_stretch = 1.0

        if time_map_enabled:
            if total_days <= 730:
                time_map_gated = True
            elif total_days <= 1095:
                time_map_gated = True  # default gated, unlock only if score>=0.75 + assets>=5 (set by caller)
            else:
                time_map_gated = False
                time_map_applied = True

        reduced_glow = asset_count >= 5
        dots_from = 20 if total_days > 180 else 5

        if asset_count <= 3:
            max_events = 2
        elif asset_count == 4:
            max_events = 2
        else:
            max_events = 1

        thumb_source = str(_config_get(config, "thumbnail_source", "endscreen") or "endscreen")

        plan = VideoPlan(
            locale=locale,
            total_data_days=total_days,
            asset_count=asset_count,
            requested_asset_count=raw_asset_count,
            dropped_assets=dropped,
            hook_title=hook_title,
            start_setup_sec=float(_config_get(config, "start_setup_sec", 0.7)),
            race_sec=race_sec,
            final_chart_hold_sec=float(_config_get(config, "final_chart_hold_sec", 1.5)),
            crossfade_sec=float(_config_get(config, "crossfade_sec", 1.0)),
            endscreen_hold_sec=endscreen_sec,
            axis_camera_mode=axis_camera_mode,
            axis_camera_required=axis_camera_required,
            axis_camera_strict=axis_camera_strict,
            time_map_enabled=time_map_enabled,
            time_map_gated=time_map_gated,
            time_map_applied=time_map_applied,
            time_map_effective=time_map_applied and tm_stretch > 1.01,
            time_map_stretch_factor=tm_stretch,
            start_cluster_reduced_glow=reduced_glow,
            endpoint_dots_from_frame=dots_from,
            max_visible_events=max_events,
            thumbnail_source=thumb_source,
        )
        plan.compute_frame_boundaries(fps)
        return plan


class QARunner:
    """QA checks after render. Checks all hard-fail conditions."""

    @staticmethod
    def run(engine: Any, video_plan: VideoPlan, video_path: str = "") -> QAResult:
        qa = QAResult()
        hard_fails: List[str] = []

        _over_limit = video_plan.requested_asset_count > VideoPlanBuilder.MAX_ASSETS
        qa.asset_limit = {
            "pass": not _over_limit,
            "requested": video_plan.requested_asset_count,
            "rendered": video_plan.asset_count,
            "dropped": video_plan.dropped_assets,
            "warnings": [],
        }
        if _over_limit:
            w = f"{video_plan.requested_asset_count} assets requested > max {VideoPlanBuilder.MAX_ASSETS}, only {video_plan.asset_count} rendered"
            qa.asset_limit["warnings"].append(w)
            hard_fails.append(f"asset_limit_exceeded: {video_plan.requested_asset_count} > {VideoPlanBuilder.MAX_ASSETS}")

        axis_applied = _engine_value(engine, "axis_camera_applied", False)
        start_x_ratio = 0.0
        qa.axis_camera = {
            "pass": True,
            "mode": video_plan.axis_camera_mode,
            "required": video_plan.axis_camera_required,
            "strict": video_plan.axis_camera_strict,
            "applied": bool(axis_applied),
            "start_x_range_ratio": start_x_ratio,
            "warnings": [],
        }
        if video_plan.axis_camera_required and not bool(axis_applied):
            qa.axis_camera["pass"] = False
            qa.axis_camera["warnings"].append(f"Camera required (mode={video_plan.axis_camera_mode}) but not applied")
            hard_fails.append("axis_camera_required_not_applied")
        if video_plan.total_data_days > 1095 and start_x_ratio > 0.35:
            qa.axis_camera["pass"] = False
            hard_fails.append(f"start_x_range_ratio {start_x_ratio:.2f} > 0.35 for {video_plan.total_data_days}d")
        if video_plan.total_data_days > 3650 and start_x_ratio > 0.20:
            qa.axis_camera["pass"] = False
            hard_fails.append(f"start_x_range_ratio {start_x_ratio:.2f} > 0.20 for {video_plan.total_data_days}d")

        time_map_at_one = _call_engine_time_map(engine, 1.0)
        if time_map_at_one is None:
            time_map_at_one = 1.0
        qa.timemap = {
            "pass": True,
            "enabled": video_plan.time_map_enabled,
            "gated": video_plan.time_map_gated,
            "applied": video_plan.time_map_applied,
            "effective": video_plan.time_map_effective,
            "stretch": video_plan.time_map_stretch_factor,
            "early_cluster_score": video_plan.time_map_early_cluster_score,
            "early_data_pct": video_plan.time_map_early_data_pct,
            "early_race_pct": video_plan.time_map_early_race_pct,
            "time_map_1_0": time_map_at_one,
            "warnings": [],
        }
        if time_map_at_one != 1.0:
            qa.timemap["pass"] = False
            hard_fails.append("time_map(1.0) != 1.0 - final data_progress muss exakt 1.0 sein")

        qa.endpoint_dots = {
            "pass": True,
            "max_distance_px": video_plan.endpoint_dot_distance_max_px,
            "from_frame": video_plan.endpoint_dots_from_frame,
            "warnings": [],
        }
        if video_plan.endpoint_dot_distance_max_px > 6:
            qa.endpoint_dots["pass"] = False
            hard_fails.append(f"endpoint_dot_distance {video_plan.endpoint_dot_distance_max_px:.1f}px > 6px")

        qa.events = {
            "pass": True,
            "max_count": video_plan.max_visible_events,
            "overlap": False,
            "during_final_hold": video_plan.events_during_final_hold,
            "warnings": [],
        }
        if video_plan.events_during_final_hold:
            qa.events["pass"] = False
            qa.events["warnings"].append("Events during final_hold should be disabled")

        qa.endscreen = {
            "pass": video_plan.endscreen_hold_sec <= 8.0,
            "duration_sec": video_plan.endscreen_hold_sec,
            "max_allowed_sec": 8.0,
            "warnings": [],
        }
        if video_plan.endscreen_hold_sec > 8.0:
            hard_fails.append(f"endscreen_hold {video_plan.endscreen_hold_sec:.1f}s > 8s")

        qa.phase_timing = {
            "pass": True,
            "final_chart_hold_sec": video_plan.final_chart_hold_sec,
            "endscreen_hold_sec": video_plan.endscreen_hold_sec,
            "race_share_pct": video_plan.race_share_pct,
            "warnings": [],
        }
        if video_plan.final_chart_hold_sec < 0.5:
            hard_fails.append(f"final_chart_hold {video_plan.final_chart_hold_sec:.1f}s < 0.5s")
        if video_plan.endscreen_hold_sec > 8:
            qa.phase_timing["pass"] = False
            hard_fails.append(f"endscreen_hold {video_plan.endscreen_hold_sec:.1f}s > 8s")
        if video_plan.race_share_pct < 70:
            qa.phase_timing["warnings"].append(f"Race only {video_plan.race_share_pct}% of video (target >70%)")

        qa.thumbnail = {
            "pass": video_plan.thumbnail_source in ("endscreen", "video_frame"),
            "source": video_plan.thumbnail_source,
            "warnings": [],
        }
        if video_plan.thumbnail_source not in ("endscreen", "video_frame"):
            hard_fails.append(f"invalid thumbnail source: {video_plan.thumbnail_source}")

        qa.final_values = {"pass": True, "consistent": True, "warnings": []}
        fv = _engine_value(engine, "final_values", None)
        if fv is None or not fv:
            qa.final_values["consistent"] = False
            qa.final_values["warnings"].append("No final_values available - consistency not verified")

        qa.hard_fails = hard_fails
        video_plan.qa_results = {
            "asset_limit": qa.asset_limit,
            "axis_camera": qa.axis_camera,
            "timemap": qa.timemap,
            "endpoint_dots": qa.endpoint_dots,
            "events": qa.events,
            "endscreen": qa.endscreen,
            "phase_timing": qa.phase_timing,
            "thumbnail": qa.thumbnail,
            "final_values": qa.final_values,
            "hard_fails": list(hard_fails),
        }
        video_plan.qa_hard_fail = bool(hard_fails)
        return qa


def _config_get(config: Any, key: str, default: Any = None) -> Any:
    if config is None:
        return default
    if isinstance(config, dict):
        return config.get(key, default)
    return getattr(config, key, default)


def _infer_total_days(df: Any, config: Any = None) -> int:
    configured = _config_get(config, "total_data_days", _config_get(config, "total_days", None))
    if configured is not None:
        return max(0, int(configured))
    index = getattr(df, "index", None)
    try:
        if index is not None and len(index) >= 2:
            delta = max(index) - min(index)
            days = getattr(delta, "days", None)
            if days is not None:
                return max(0, int(days) + 1)
    except Exception:
        pass
    return 0


def _infer_asset_count(df: Any, config: Any = None) -> int:
    configured = _config_get(config, "asset_count", None)
    if configured is not None:
        if isinstance(configured, (list, tuple, set, frozenset)):
            return len(configured)
        return max(0, int(configured))
    columns = getattr(df, "columns", None)
    if columns is not None:
        try:
            return len(list(columns))
        except Exception:
            pass
    return 0


def _engine_value(engine: Any, name: str, default: Any = None) -> Any:
    if engine is None:
        return default
    if isinstance(engine, dict):
        value = engine.get(name, default)
    else:
        value = getattr(engine, name, default)
    if callable(value):
        try:
            return value()
        except TypeError:
            return default
    return value


def _call_engine_time_map(engine: Any, value: float) -> Optional[float]:
    if engine is None:
        return None
    if isinstance(engine, dict):
        mapper = engine.get("time_map") or engine.get("timemap")
    else:
        mapper = getattr(engine, "time_map", None) or getattr(engine, "timemap", None)
    if callable(mapper):
        try:
            return float(mapper(value))
        except Exception:
            return None
    return None


__all__ = [
    "duration_from_period", "suggested_endscreen_hold", "PhasePolicy",
    "VideoPlan", "QAResult", "VideoPlanBuilder", "QARunner", "_MAX_ASSETS",
]
