"""build_scene_plan — wires data -> camera -> timemap -> events -> planning into a ScenePlan.

This is the Brain's single entry point. CLI and any future caller (e.g. a batch
job) should go through build_scene_plan rather than calling the submodules directly.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

import pandas as pd

from . import camera as camera_mod
from . import data as data_mod
from . import events as events_mod
from . import planning as planning_mod
from . import timemap as timemap_mod
from .advisory import check_advisory_wording
from .scene_plan import (
    Camera,
    CameraKeyframeOut,
    DataSeries,
    Duration,
    Endscreen,
    EventOut,
    FinalValue,
    HookVariant,
    Phase,
    Phases,
    QA,
    QAResultEntry,
    ScenePlan,
    Theme,
    ThemeColors,
    TimeMap,
    TimeMapControlPoint,
    Topic,
)

# Fallback palette when a theme doesn't specify per-ticker colors — same source as
# value_racer_video.py's COLOR_PALETTE first slots, trimmed to common cases.
_DEFAULT_COLOR_PALETTE = [
    "#FFD700", "#00E5FF", "#FF4444", "#33FF99", "#A855F7", "#4488FF", "#FF8800", "#22DDAA",
]


def _default_theme_dict() -> Dict[str, Any]:
    return {
        "id": "default_dark",
        "colors": {
            "bg": {"primary": "#080c14", "secondary": "#0f1623"},
            "text": {"primary": "#FFFFFF", "secondary": "#AAAAAA"},
            "accent": {"primary": "#00E5FF"},
        },
        "font_family": "Inter",
        "glow_mode": "full",
        "event_styles": {
            et.value: {"color": style.accent_color, "pulse": style.pulse}
            for et, style in events_mod.STYLES.items()
        },
    }


def build_scene_plan(topic_brief: dict, theme: dict, hook_variant: dict) -> ScenePlan:
    """Build a complete ScenePlan from a topic brief.

    topic_brief: {"assets": [...], "period_days": int, "locale": "de",
                   "fps": 30, "investment": 1000, "hook_title": "...",
                   "events": [...], "mode": "evergreen"|"news"}
    theme: dict matching the `theme` block shape (id/colors/font_family/glow_mode/event_styles);
           an empty dict falls back to _default_theme_dict().
    hook_variant: dict matching {"id": "..."}.
    """
    assets: List[str] = list(topic_brief["assets"])
    period_days: int = int(topic_brief.get("period_days", 1825))
    locale: str = topic_brief.get("locale", "de")
    fps: int = int(topic_brief.get("fps", 30))
    investment: float = float(topic_brief.get("investment", 1000))
    hook_title: str = topic_brief.get("hook_title", "")
    mode: str = topic_brief.get("mode", "evergreen")
    raw_events = topic_brief.get("events", [])

    end_date = pd.Timestamp.utcnow().tz_localize(None).normalize()
    start_date = end_date - pd.Timedelta(days=period_days)

    # 1. Data
    download = data_mod.download_data_sync(
        tickers=assets, start_date=start_date, end_date=end_date,
        investment=investment, mode=mode,
    )
    df = download.df
    actual_days = max(0, (df.index[-1] - df.index[0]).days)

    # 2. Planning (duration/phases) — drives camera/event frame ranges.
    video_plan = planning_mod.VideoPlanBuilder.build(
        df, config={"total_data_days": actual_days, "hook_title": hook_title}, fps=fps, locale=locale,
    )

    intro_end = video_plan.phase_start_end
    race_end = video_plan.phase_race_end
    final_hold_end = video_plan.phase_final_end
    # Brain's contract has no separate crossfade phase; fold crossfade time into
    # endscreen since the renderer treats frames as the only time unit anyway.
    endscreen_end = video_plan.phase_endscreen_end

    # 3. Camera
    policy = camera_mod.detect_policy(df, investment=investment, mode_hint=mode)
    cam_plan = camera_mod.CameraPlanBuilder.build(df, investment=investment, policy=policy)
    cam_keyframes = camera_mod.keyframes_to_race_frames(cam_plan, intro_end, race_end)

    # 4. TimeMap
    cluster = timemap_mod.analyze_early_cluster(df)
    time_map_obj = timemap_mod.score_to_time_map(
        cluster["early_cluster_score"], cluster["early_data_pct"], cluster.get("early_volatility", 0.0),
    )
    time_map_enabled = video_plan.time_map_enabled and not video_plan.time_map_gated
    control_points = (
        timemap_mod.build_control_points(time_map_obj, intro_end, race_end)
        if time_map_enabled
        else [{"frame": intro_end, "data_index": 0.0}, {"frame": race_end, "data_index": 1.0}]
    )

    # 5. Events — video_plan-like dict exposes the frame fields EventBeatBuilder/EventQA expect.
    event_plan_ctx = {
        "total_frames": endscreen_end,
        "fps": fps,
        "max_visible_events": video_plan.max_visible_events,
        "final_hold_start_frame": race_end,
        "final_hold_end_frame": final_hold_end,
        "crossfade_start_frame": final_hold_end,
        "crossfade_end_frame": final_hold_end,
        "endscreen_start_frame": final_hold_end,
        "endscreen_end_frame": endscreen_end,
    }
    beats = events_mod.EventBeatBuilder.build(raw_events, df, assets, video_plan=event_plan_ctx, locale=locale, fps=fps)
    # Rescale beat frames (computed against 0..len(df)-1 data positions mapped into
    # event_plan_ctx["total_frames"]) onto the race phase specifically, then clamp
    # so no event beat can land in final_hold/endscreen — this is the hard QA gate.
    for b in beats:
        if b.skipped:
            continue
        scale = (race_end - intro_end) / max(1, endscreen_end)
        b.start_frame = intro_end + int(round(b.start_frame * scale))
        b.peak_frame = intro_end + int(round(b.peak_frame * scale))
        b.end_frame = intro_end + int(round(b.end_frame * scale))
        if b.end_frame >= race_end:
            overflow = b.end_frame - race_end + 1
            b.end_frame -= overflow
            b.peak_frame = min(b.peak_frame, b.end_frame)
            b.start_frame = min(b.start_frame, b.peak_frame)

    event_qa = events_mod.EventQA.run_qa(beats, video_plan=event_plan_ctx)

    # 6. QA aggregation
    advisory = check_advisory_wording(hook_title)
    qa_results: List[QAResultEntry] = []
    qa_results.append(QAResultEntry(
        check="advisory_wording", passed=not advisory["flagged"],
        detail="; ".join(advisory["warnings"]) if advisory["flagged"] else "ok",
    ))
    qa_results.append(QAResultEntry(
        check="event_overlap_final_hold_endscreen",
        passed=not (event_qa["event_labels_during_final_hold"] or event_qa["event_labels_during_endscreen"]),
        detail="; ".join(event_qa["hard_fails"]) if event_qa["hard_fails"] else "ok",
    ))
    qa_results.append(QAResultEntry(
        check="event_collisions_resolved", passed=event_qa["event_collisions_resolved"],
        detail="ok" if event_qa["event_collisions_resolved"] else "unresolved collisions",
    ))
    qa_results.append(QAResultEntry(
        check="asset_count", passed=len(df.columns) >= 2,
        detail=f"{len(df.columns)} valid tickers after filtering",
    ))
    qa_results.append(QAResultEntry(
        check="time_map_endpoint", passed=(time_map_obj.map(1.0) == 1.0),
        detail="data_progress(1.0) must equal 1.0 exactly",
    ))

    hard_fail = any(not r.passed for r in qa_results if r.check in (
        "event_overlap_final_hold_endscreen", "event_collisions_resolved", "asset_count", "time_map_endpoint",
    ))

    # 7. Assemble ScenePlan
    theme_dict = theme if theme else _default_theme_dict()
    palette = {t: _DEFAULT_COLOR_PALETTE[i % len(_DEFAULT_COLOR_PALETTE)] for i, t in enumerate(df.columns)}

    data_series = [
        DataSeries(
            ticker=ticker,
            label=data_mod.format_ticker_label(ticker),
            color=palette[ticker],
            dates=[d.strftime("%Y-%m-%d") for d in df.index],
            values=[None if pd.isna(v) else round(float(v), 6) for v in df[ticker]],
        )
        for ticker in df.columns
    ]

    camera_out = Camera(
        policy=policy.mode,
        keyframes=[
            CameraKeyframeOut(frame=kf.frame, x_min=kf.x_min, x_max=kf.x_max, y_min=kf.y_min, y_max=kf.y_max)
            for kf in cam_keyframes
        ],
    )

    time_map_out = TimeMap(
        enabled=time_map_enabled,
        control_points=[TimeMapControlPoint(**cp) for cp in control_points],
    )

    events_out = [
        EventOut(
            frame_start=b.start_frame, frame_end=b.end_frame, ticker=b.ticker,
            type=b.event_type.value, label=(b.label_primary or b.label_secondary or "")[:42],
            style_ref=b.event_type.value,
        )
        for b in beats if not b.skipped
    ]

    final_values = [
        FinalValue(
            ticker=ticker,
            value=round(download.stats[ticker].final_value, 2),
            gain_pct=round((download.stats[ticker].final_value / investment - 1) * 100, 2),
        )
        for ticker in df.columns if ticker in download.stats
    ]

    return ScenePlan(
        video_id=str(uuid.uuid4()),
        topic=Topic(assets=assets, period_days=period_days, locale=locale),
        fps=fps,
        duration=Duration(
            total_frames=endscreen_end,
            total_duration_sec=round(endscreen_end / fps, 3),
            phases=Phases(
                intro=Phase(start_frame=0, end_frame=intro_end),
                race=Phase(start_frame=intro_end, end_frame=race_end),
                final_hold=Phase(start_frame=race_end, end_frame=final_hold_end),
                endscreen=Phase(start_frame=final_hold_end, end_frame=endscreen_end),
            ),
        ),
        data_series=data_series,
        camera=camera_out,
        time_map=time_map_out,
        events=events_out,
        theme=Theme(
            id=theme_dict["id"], colors=ThemeColors(**theme_dict["colors"]),
            font_family=theme_dict["font_family"], glow_mode=theme_dict["glow_mode"],
            event_styles=theme_dict["event_styles"],
        ),
        hook_variant=HookVariant(id=hook_variant.get("id", "default")),
        endscreen=Endscreen(final_values=final_values, thumbnail_source_frame=race_end),
        qa=QA(hard_fail=hard_fail, results=qa_results),
    )
