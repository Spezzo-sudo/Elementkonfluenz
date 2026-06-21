"""Camera planning — ported from value_racer_video.py CameraPlanBuilder & friends.

Renderer-facing output is frame/axis-bounds only (camera.keyframes = list of
{frame, x_min, x_max, y_min, y_max}), so x-axis bounds are expressed as data-index
positions (0..len(df)-1) rather than matplotlib date2num floats — the original
used mdates.date2num purely to get a continuous x-axis number, which we get for
free from positional index here. Renderer maps frame->position itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import pandas as pd


@dataclass
class AxisCameraPolicy:
    """Camera profile. One profile per video type / asset class.

    mode:
        stock_value     — absolute values from $1000 (ValueRacer default)
        percent         — percent change from 0% (news/index)
        high_volatility — high volatility (crypto, penny stocks)
    """

    mode: str = "stock_value"
    min_y_range_pct: float = 0.20
    y_padding_pct: float = 0.08
    early_window_min_days: int = 90
    early_window_max_days: int = 365
    early_window_pct: float = 0.12
    lookahead_pct: float = 0.06
    zoomout_start_progress: float = 0.80
    keyframe_strategy: str = "hybrid"  # "fixed" | "hybrid"
    expand_alpha: float = 0.30
    contract_alpha: float = 0.05


STOCK_VALUE_POLICY = AxisCameraPolicy(
    mode="stock_value", min_y_range_pct=0.20, y_padding_pct=0.10,
    early_window_min_days=90, early_window_max_days=365, early_window_pct=0.12,
    lookahead_pct=0.06, zoomout_start_progress=0.80, keyframe_strategy="hybrid",
    expand_alpha=0.30, contract_alpha=0.05,
)

PERCENT_POLICY = AxisCameraPolicy(
    mode="percent", min_y_range_pct=0.10, y_padding_pct=0.12,
    early_window_min_days=30, early_window_max_days=180, early_window_pct=0.10,
    lookahead_pct=0.08, zoomout_start_progress=0.85, keyframe_strategy="hybrid",
    expand_alpha=0.35, contract_alpha=0.08,
)

HIGH_VOLATILITY_POLICY = AxisCameraPolicy(
    mode="high_volatility", min_y_range_pct=0.40, y_padding_pct=0.15,
    early_window_min_days=30, early_window_max_days=180, early_window_pct=0.08,
    lookahead_pct=0.10, zoomout_start_progress=0.75, keyframe_strategy="hybrid",
    expand_alpha=0.40, contract_alpha=0.03,
)


def detect_policy(df: pd.DataFrame, investment: float = 1000.0, mode_hint: Optional[str] = None) -> AxisCameraPolicy:
    """Auto-detect the matching camera profile from the data."""
    if mode_hint in ("percent", "news"):
        return PERCENT_POLICY

    if df is None or df.empty:
        return STOCK_VALUE_POLICY

    first_row = df.iloc[0]
    start_median = float(first_row.median())
    final_row = df.iloc[-1]
    final_median = float(final_row.median())

    daily_returns = df.pct_change().abs().mean().mean()
    is_high_vol = daily_returns > 0.05 if not pd.isna(daily_returns) else False
    is_percent_like = abs(start_median) < 50 and abs(final_median) < 500

    if is_high_vol:
        return HIGH_VOLATILITY_POLICY
    if is_percent_like:
        return PERCENT_POLICY
    return STOCK_VALUE_POLICY


@dataclass
class DataShapeAnalysis:
    total_days: int = 0
    asset_count: int = 0
    start_value_median: float = 1000.0
    global_min: float = 0.0
    global_max: float = 0.0
    volatility_score: float = 0.0
    divergence_progress: float = 0.0
    first_2x_progress: float = 1.0
    max_drawdown_progress: float = 0.0
    is_percent_like: bool = False
    is_high_volatility: bool = False


def analyze_data_shape(df: pd.DataFrame, investment: float = 1000.0) -> DataShapeAnalysis:
    if df is None or df.empty:
        return DataShapeAnalysis()

    index = df.index
    total_days = (index[-1] - index[0]).days
    asset_count = len(df.columns)
    start_median = float(df.iloc[0].median())
    global_min = float(df.min(skipna=True).min(skipna=True))
    global_max = float(df.max(skipna=True).max(skipna=True))

    daily_returns = df.pct_change().abs().mean().mean()
    volatility_score = float(daily_returns) if not pd.isna(daily_returns) else 0.0

    divergence_progress = 1.0
    for i in range(len(df)):
        row = df.iloc[i]
        if len(row) >= 2:
            min_v, max_v = float(row.min()), float(row.max())
            mid = (min_v + max_v) / 2.0
            if mid > 0 and (max_v - min_v) / mid > 0.10:
                divergence_progress = i / max(1, len(df) - 1)
                break

    first_2x_progress = 1.0
    threshold = investment * 2
    for i in range(len(df)):
        if float(df.iloc[i].max()) >= threshold:
            first_2x_progress = i / max(1, len(df) - 1)
            break

    rolling_max = df.expanding().max()
    dd = (df - rolling_max) / rolling_max
    dd_min_pos = dd.min().min()
    dd_idx = dd.stack().idxmin() if not dd.empty else None
    max_drawdown_progress = 0.0
    if dd_idx is not None and not pd.isna(dd_min_pos) and dd_min_pos < 0:
        try:
            pos = index.get_loc(dd_idx[0]) if isinstance(dd_idx, tuple) else 0
            max_drawdown_progress = pos / max(1, len(index) - 1)
        except (KeyError, TypeError):
            pass

    return DataShapeAnalysis(
        total_days=total_days, asset_count=asset_count,
        start_value_median=float(start_median),
        global_min=global_min, global_max=global_max,
        volatility_score=volatility_score,
        divergence_progress=divergence_progress,
        first_2x_progress=first_2x_progress,
        max_drawdown_progress=max_drawdown_progress,
        is_percent_like=abs(start_median) < 50,
        is_high_volatility=volatility_score > 0.05,
    )


def _adjust_keyframes(base_progresses: List[float], shape: DataShapeAnalysis, max_shift: float = 0.10) -> List[float]:
    """Shift base keyframes [0, .20, .50, .80, 1.0] based on data shape (divergence point, early 2x growth)."""
    adjusted = list(base_progresses)
    if shape.divergence_progress < 1.0 and len(adjusted) >= 3:
        mid_target = min(shape.divergence_progress + 0.10, 0.60)
        shift = min(abs(mid_target - 0.50), max_shift)
        adjusted[2] = 0.50 + shift * (1 if mid_target > 0.50 else -1)
        if shape.divergence_progress > 0.25 and len(adjusted) >= 2:
            early_shift = min(abs(shape.divergence_progress * 0.6 - 0.20), max_shift * 0.5)
            adjusted[1] = 0.20 + early_shift

    if shape.first_2x_progress < 1.0 and len(adjusted) >= 3:
        if shape.first_2x_progress < 0.30:
            adjusted[3] = max(0.70, adjusted[3] - 0.05)

    return adjusted


@dataclass
class CameraKeyframe:
    """A planned camera state at a given frame. x bounds are data-index positions (0..len(df)-1)."""

    frame: int = 0
    x_min: float = 0.0
    x_max: float = 0.0
    y_min: float = 0.0
    y_max: float = 0.0
    camera_phase: str = "race"
    easing: str = "ease_out_cubic"


@dataclass
class CameraPlan:
    keyframes: List[CameraKeyframe] = field(default_factory=list)
    x_mode: str = "fixed_full_period"
    total_days: int = 0
    early_window_days: int = 90
    warnings: List[str] = field(default_factory=list)
    policy_mode: str = "stock_value"


class CameraPlanBuilder:
    """Builds a CameraPlan from final data + policy. Keyframe race_progress is
    converted to absolute frame numbers within the race phase by the caller
    (builder.py), since only it knows the race phase's frame range."""

    @staticmethod
    def build(df: pd.DataFrame, investment: float = 1000.0, policy: Optional[AxisCameraPolicy] = None) -> CameraPlan:
        if df is None or df.empty:
            return CameraPlan(warnings=["Keine Daten fuer CameraPlan"])

        if policy is None:
            policy = STOCK_VALUE_POLICY
        shape = analyze_data_shape(df, investment)

        index = df.index
        total_days = (index[-1] - index[0]).days
        n = len(df)

        x_mode = "fixed_full_period" if total_days <= 540 else "progressive_reveal_then_full_zoomout"

        early_window_days = max(
            policy.early_window_min_days,
            min(int(total_days * policy.early_window_pct), policy.early_window_max_days),
        )

        plan = CameraPlan(
            keyframes=[], x_mode=x_mode, total_days=total_days,
            early_window_days=early_window_days, warnings=[], policy_mode=policy.mode,
        )

        def _y_for_window(left_pos: int, right_pos: int) -> tuple[float, float]:
            visible = df.iloc[max(0, left_pos):right_pos + 1]
            if visible.empty:
                return float(investment * 0.9), float(investment * 1.1)
            y_min_v = float(visible.min(skipna=True).min(skipna=True))
            y_max_v = float(visible.max(skipna=True).max(skipna=True))
            mid = (y_min_v + y_max_v) / 2.0
            raw_range = y_max_v - y_min_v
            min_range = max(mid * policy.min_y_range_pct, 10.0)
            if raw_range < min_range:
                y_min_v = mid - min_range / 2.0
                y_max_v = mid + min_range / 2.0
            y_range = y_max_v - y_min_v
            y_min = y_min_v - y_range * policy.y_padding_pct
            y_max = y_max_v + y_range * policy.y_padding_pct
            if policy.mode == "stock_value" and y_min_v >= 0:
                y_min_floor = max(0, y_min_v * 0.6)
                y_min = max(y_min_floor, y_min)
            return y_min, y_max

        x_pad = max(2, int(n * 0.015))
        full_x_min, full_x_max = -x_pad, (n - 1) + x_pad

        if x_mode == "fixed_full_period":
            y_min, y_max = _y_for_window(0, n - 1)
            plan.keyframes.append(CameraKeyframe(frame=0, x_min=full_x_min, x_max=full_x_max,
                                                   y_min=y_min, y_max=y_max, camera_phase="full", easing="linear"))
            plan.keyframes.append(CameraKeyframe(frame=1, x_min=full_x_min, x_max=full_x_max,
                                                   y_min=y_min, y_max=y_max, camera_phase="full", easing="linear"))
        else:
            lookahead = max(30, int(total_days * policy.lookahead_pct))
            # lookahead is in days; convert to a data-index step using avg days/point.
            days_per_point = total_days / max(1, n - 1)
            lookahead_pts = max(1, int(round(lookahead / max(days_per_point, 1e-9))))

            base_progresses = [0.0, 0.20, 0.50, 0.80, 1.0]
            p = _adjust_keyframes(base_progresses, shape) if policy.keyframe_strategy == "hybrid" else base_progresses

            def pos_at(progress: float) -> int:
                return int(round(progress * (n - 1)))

            kf1_xmax = min(n - 1, lookahead_pts)
            y1_min, y1_max = _y_for_window(0, kf1_xmax)
            plan.keyframes.append(CameraKeyframe(frame=pos_at(p[0]), x_min=0, x_max=kf1_xmax,
                                                   y_min=y1_min, y_max=y1_max, camera_phase="start", easing="ease_out_cubic"))

            kf2_pos = pos_at(p[1])
            kf2_xmax = min(n - 1, kf2_pos + int(lookahead_pts * 1.5))
            y2_min, y2_max = _y_for_window(0, kf2_xmax)
            plan.keyframes.append(CameraKeyframe(frame=kf2_pos, x_min=0, x_max=kf2_xmax,
                                                   y_min=y2_min, y_max=y2_max, camera_phase="early", easing="ease_out_cubic"))

            kf3_pos = pos_at(p[2])
            kf3_xmax = min(n - 1, kf3_pos + int(lookahead_pts * 2))
            y3_min, y3_max = _y_for_window(0, kf3_xmax)
            plan.keyframes.append(CameraKeyframe(frame=kf3_pos, x_min=0, x_max=kf3_xmax,
                                                   y_min=y3_min, y_max=y3_max, camera_phase="mid", easing="ease_out_cubic"))

            zoomout_at = min(p[3], policy.zoomout_start_progress + 0.05)
            y4_min, y4_max = _y_for_window(0, n - 1)
            plan.keyframes.append(CameraKeyframe(frame=pos_at(zoomout_at), x_min=full_x_min, x_max=full_x_max,
                                                   y_min=y4_min, y_max=y4_max, camera_phase="late", easing="ease_in_out_cubic"))

            final_progress = max(p[4], zoomout_at + 0.05)
            plan.keyframes.append(CameraKeyframe(frame=pos_at(min(final_progress, 1.0)), x_min=full_x_min, x_max=full_x_max,
                                                   y_min=y4_min, y_max=y4_max, camera_phase="full_chart", easing="linear"))

        if len(plan.keyframes) < 2:
            plan.warnings.append(f"Nur {len(plan.keyframes)} Keyframes (min 2)")
        if x_mode != "fixed_full_period":
            first, last = plan.keyframes[0], plan.keyframes[-1]
            if (first.x_max - first.x_min) >= (last.x_max - last.x_min):
                plan.warnings.append("Early window ist nicht kleiner als full range")

        return plan


def keyframes_to_race_frames(plan: CameraPlan, race_start_frame: int, race_end_frame: int) -> List[CameraKeyframe]:
    """Rescale keyframe.frame (a 0..n-1 data-index race_progress proxy) into absolute
    timeline frames within [race_start_frame, race_end_frame). Camera only moves during
    the race phase per the contract; intro/final_hold/endscreen hold the last camera state.
    """
    if not plan.keyframes:
        return []
    max_idx = max(kf.frame for kf in plan.keyframes) or 1
    span = max(1, race_end_frame - race_start_frame)
    out = []
    for kf in plan.keyframes:
        progress = kf.frame / max_idx if max_idx else 0.0
        abs_frame = race_start_frame + int(round(progress * span))
        out.append(CameraKeyframe(
            frame=abs_frame, x_min=kf.x_min, x_max=kf.x_max, y_min=kf.y_min, y_max=kf.y_max,
            camera_phase=kf.camera_phase, easing=kf.easing,
        ))
    return out
