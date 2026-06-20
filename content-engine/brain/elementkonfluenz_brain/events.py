"""EventBeat system — ported near-verbatim from event_beat.py.

Already dependency-light (stdlib only, accepts pandas-like inputs without
importing pandas) in the source; only changes here are extracting EventQA's
final_hold/endscreen overlap window from a generic dict instead of a VideoPlan
instance, since the Brain's planning.py VideoPlan has different field names.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


class EventType(Enum):
    """Supported ValueRacer event categories."""

    geopolitical_risk = "geopolitical_risk"
    energy_shock = "energy_shock"
    financial_crisis = "financial_crisis"
    ath_record = "ath_record"
    macro_rate = "macro_rate"
    earnings = "earnings"
    crash = "crash"
    default = "default"


@dataclass
class EventVisualStyle:
    """Visual rendering style for an event beat."""

    accent_color: str
    line_width: float = 1.0
    line_alpha: float = 0.25
    badge_bg_alpha: float = 0.25
    pulse: bool = True
    glow_color: Optional[str] = None


STYLES: Dict[EventType, EventVisualStyle] = {
    EventType.geopolitical_risk: EventVisualStyle(
        accent_color="#f59e0b", line_width=1.0, line_alpha=0.22, badge_bg_alpha=0.24, pulse=True, glow_color="#fbbf24"
    ),
    EventType.energy_shock: EventVisualStyle(
        accent_color="#f97316", line_width=1.2, line_alpha=0.28, badge_bg_alpha=0.28, pulse=True, glow_color="#fb923c"
    ),
    EventType.financial_crisis: EventVisualStyle(
        accent_color="#ef4444", line_width=1.5, line_alpha=0.35, badge_bg_alpha=0.32, pulse=True, glow_color="#f87171"
    ),
    EventType.ath_record: EventVisualStyle(
        accent_color="#00E5FF", line_width=1.0, line_alpha=0.18, badge_bg_alpha=0.18, pulse=False, glow_color=None
    ),
    EventType.macro_rate: EventVisualStyle(
        accent_color="#a855f7", line_width=1.0, line_alpha=0.25, badge_bg_alpha=0.23, pulse=True, glow_color="#c084fc"
    ),
    EventType.earnings: EventVisualStyle(
        accent_color="#4488FF", line_width=1.0, line_alpha=0.22, badge_bg_alpha=0.22, pulse=False, glow_color=None
    ),
    EventType.crash: EventVisualStyle(
        accent_color="#dc2626", line_width=2.0, line_alpha=0.45, badge_bg_alpha=0.35, pulse=True, glow_color="#ef4444"
    ),
    EventType.default: EventVisualStyle(
        accent_color="#888888", line_width=1.0, line_alpha=0.25, badge_bg_alpha=0.25, pulse=True, glow_color=None
    ),
}


@dataclass
class EventBeat:
    """A validated, render-ready event annotation."""

    event_id: str
    event_type: EventType = EventType.default
    ticker: Optional[str] = None
    scope: str = "market"  # ticker_specific|sector|market|macro|global
    event_date_original: str = ""
    event_date_mapped: Any = None
    label_primary: str = ""
    label_secondary: str = ""
    severity: str = "medium"  # low|medium|high
    visual_style: Any = None
    priority: int = 5
    collision_priority: int = 5
    start_frame: int = 0
    peak_frame: int = 0
    end_frame: int = 0
    fade_in_frames: int = 9
    hold_frames: int = 45
    fade_out_frames: int = 15
    marker_only_after_end: bool = False
    rendered: bool = False
    skipped: bool = False
    skip_reason: Optional[str] = None
    marker_only: bool = False
    collision_status: Optional[str] = None
    final_position: Optional[tuple] = None


class EventTextGenerator:
    """German market-aware label generation for EventBeat objects."""

    DE_KEYWORD_LABELS: Tuple[Tuple[str, Tuple[str, str]], ...] = (
        ("krieg", ("Krisen-Schock", "Risiko steigt")),
        ("crash", ("Crash", "Markt kippt")),
        ("corona", ("Corona-Krise", "Weltweit lockdown")),
        ("gold", ("Gold-Rallye", "Sicherer Hafen")),
        ("öl", ("Öl-Schock", "Energiepreise steigen")),
        ("oel", ("Öl-Schock", "Energiepreise steigen")),
        ("oil", ("Öl-Schock", "Energiepreise steigen")),
        ("tech", ("KI-Boom", "Tech zieht an")),
        ("ki", ("KI-Boom", "Tech-Rallye")),
        ("ai", ("KI-Boom", "Tech-Rallye")),
        ("zins", ("Zinsentscheid", "Fed bewegt Markt")),
        ("rate", ("Zinsentscheid", "Fed bewegt Markt")),
        ("fed", ("Zinsentscheid", "Fed bewegt Markt")),
        ("inflation", ("Inflationsangst", "Geldpolitik spannt")),
        ("ath", ("Rekordhoch", "Neues ATH")),
        ("rekord", ("Rekordhoch", "Neues ATH")),
        ("banken", ("Bankenkrise", "Vertrauen fällt")),
        ("bank", ("Bankenkrise", "Vertrauen fällt")),
        ("krise", ("Krisen-Modus", "Markt unter Druck")),
        ("earnings", ("Earnings", "Zahlen bewegen")),
        ("gewinn", ("Gewinnsprung", "Starker Ausblick")),
        ("ipo", ("IPO", "Börsengang")),
        ("split", ("Aktiensplit", "Kursanpassung")),
    )

    @staticmethod
    def generate(
        original_label: Any,
        event_type: EventType,
        scope: str,
        ticker: Optional[str],
        locale: str = "de",
    ) -> Tuple[str, str]:
        """Generate primary/secondary text labels.

        If no curated keyword matches, the original label is truncated to at most
        three words and used as the primary label. Empty input returns empty labels,
        which downstream renderers can interpret as marker-only.
        """
        label = "" if original_label is None else str(original_label).strip()
        if not label:
            return "", ""

        lowered = label.lower()
        if locale.lower().startswith("de"):
            for keyword, labels in EventTextGenerator.DE_KEYWORD_LABELS:
                if keyword in lowered:
                    return labels

        words = label.split()
        primary = " ".join(words[:3])
        if len(primary) > 42:
            primary = primary[:39].rstrip() + "..."
        return primary, ""


class EventBeatBuilder:
    """Build, validate, map, dedupe and prioritize raw events."""

    TYPE_KEYWORDS: Tuple[Tuple[EventType, Tuple[str, ...]], ...] = (
        (EventType.crash, ("crash", "absturz", "selloff", "sell-off", "einbruch")),
        (EventType.geopolitical_risk, ("krieg", "war", "geopolit", "invasion", "terror", "konflikt")),
        (EventType.energy_shock, ("öl", "oel", "oil", "gas", "energie", "energy", "opec")),
        (EventType.financial_crisis, ("banken", "bank", "krise", "lehman", "credit crunch", "finanzkrise")),
        (EventType.ath_record, ("ath", "rekord", "all time high", "all-time high", "rekordhoch")),
        (EventType.macro_rate, ("zins", "rate", "fed", "ezb", "ecb", "inflation", "cpi", "geldpolitik")),
        (EventType.earnings, ("earnings", "gewinn", "zahlen", "quartal", "ipo", "split", "ausblick")),
    )

    SCOPE_PRIORITY: Dict[str, int] = {
        "manual": 0, "market": 1, "global": 1, "sector": 2, "macro": 3, "ticker_specific": 4,
    }

    SEVERITY_BONUS: Dict[str, int] = {"high": -2, "medium": 0, "low": 1}

    @classmethod
    def build(
        cls,
        raw_events: Any,
        df: Any,
        tickers: Any,
        video_plan: Any = None,
        locale: str = "de",
        fps: int = 30,
    ) -> List[EventBeat]:
        """Build EventBeat instances from raw events.

        raw_events may contain dicts or tuples: (date, label) or (date, label,
        color). Date mapping uses df.index with a tolerance of three calendar days.
        Events that cannot be mapped are returned with skipped=True so QA can report
        them. Non-skipped events are deduped by (ticker, event_type) within 40 data
        points, keeping the highest-priority beat.
        """
        index_values = cls._extract_index(df)
        if not index_values:
            return [
                EventBeat(
                    event_id=f"event_{i:03d}",
                    event_date_original=str(cls._raw_date(raw)),
                    label_primary=str(cls._raw_label(raw) or ""),
                    skipped=True,
                    skip_reason="df.index is empty or unavailable",
                    rendered=False,
                )
                for i, raw in enumerate(cls._iter_raw_events(raw_events), 1)
            ]

        index_dates = [cls._to_date(v) for v in index_values]
        beats: List[EventBeat] = []
        deduped_count = 0

        for i, raw in enumerate(cls._iter_raw_events(raw_events), 1):
            parsed = cls._parse_raw_event(raw, i)
            original_date = parsed.get("date")
            original_label = parsed.get("label", "")
            event_id = str(parsed.get("event_id") or parsed.get("id") or f"event_{i:03d}")
            ticker = cls._normalize_ticker(parsed.get("ticker"), tickers)
            scope = str(parsed.get("scope") or ("ticker_specific" if ticker else "market"))
            severity = str(parsed.get("severity") or "medium").lower()
            if severity not in {"low", "medium", "high"}:
                severity = "medium"

            event_type = cls._coerce_event_type(parsed.get("event_type")) or cls.detect_event_type(original_label)
            primary, secondary = EventTextGenerator.generate(original_label, event_type, scope, ticker, locale=locale)
            mapped_value, mapped_pos, skip_reason = cls._map_date(original_date, index_values, index_dates, tolerance_days=3)
            visual_style = cls._style_for(event_type, parsed.get("color"))
            priority = cls._priority(scope, severity, parsed)
            collision_priority = int(parsed.get("collision_priority", priority)) if cls._is_intlike(parsed.get("collision_priority")) else priority

            beat = EventBeat(
                event_id=event_id,
                event_type=event_type,
                ticker=ticker,
                scope=scope,
                event_date_original="" if original_date is None else str(original_date),
                event_date_mapped=mapped_value,
                label_primary=primary,
                label_secondary=secondary,
                severity=severity,
                visual_style=visual_style,
                priority=priority,
                collision_priority=collision_priority,
                skipped=skip_reason is not None,
                skip_reason=skip_reason,
                rendered=skip_reason is None,
                marker_only=(not primary and not secondary),
            )
            if not beat.skipped:
                cls._apply_timing(beat, mapped_pos, len(index_values), video_plan, fps)
            beats.append(beat)

        kept: List[Tuple[EventBeat, Optional[int]]] = []
        for beat in beats:
            pos = cls._index_position(beat.event_date_mapped, index_values) if not beat.skipped else None
            if beat.skipped:
                kept.append((beat, pos))
                continue

            duplicate_at: Optional[int] = None
            for idx, (existing, existing_pos) in enumerate(kept):
                if existing.skipped or existing_pos is None or pos is None:
                    continue
                if (existing.ticker, existing.event_type) == (beat.ticker, beat.event_type) and abs(existing_pos - pos) <= 40:
                    duplicate_at = idx
                    break

            if duplicate_at is None:
                kept.append((beat, pos))
            else:
                existing, existing_pos = kept[duplicate_at]
                deduped_count += 1
                winner, loser = cls._choose_winner(existing, beat)
                loser.skipped = True
                loser.rendered = False
                loser.skip_reason = "deduped within 40 data points"
                loser.collision_status = "deduped"
                if winner is beat:
                    kept[duplicate_at] = (beat, pos)
                    kept.append((loser, existing_pos))
                else:
                    kept.append((loser, pos))

        result = [b for b, _ in kept]
        for beat in result:
            if beat.skip_reason == "deduped within 40 data points":
                beat.collision_status = "deduped"
        result.sort(key=lambda b: (cls._sortable_date(b.event_date_mapped), b.priority, b.event_id))
        for beat in result:
            setattr(beat, "_deduped_count_total", deduped_count)
        return result

    @staticmethod
    def detect_event_type(label: Any) -> EventType:
        text = "" if label is None else str(label).lower()
        for event_type, keywords in EventBeatBuilder.TYPE_KEYWORDS:
            if any(keyword in text for keyword in keywords):
                return event_type
        return EventType.default

    @staticmethod
    def _iter_raw_events(raw_events: Any) -> List[Any]:
        if raw_events is None:
            return []
        if isinstance(raw_events, dict):
            if "events" in raw_events and isinstance(raw_events["events"], Iterable):
                return list(raw_events["events"])
            return [raw_events]
        return list(raw_events)

    @staticmethod
    def _parse_raw_event(raw: Any, index: int) -> Dict[str, Any]:
        if isinstance(raw, dict):
            out = dict(raw)
            if "date" not in out:
                for key in ("event_date", "time", "timestamp", "x"):
                    if key in out:
                        out["date"] = out[key]
                        break
            if "label" not in out:
                for key in ("text", "name", "title", "event", "description"):
                    if key in out:
                        out["label"] = out[key]
                        break
            return out
        if isinstance(raw, (tuple, list)):
            if len(raw) == 2:
                return {"date": raw[0], "label": raw[1]}
            if len(raw) >= 3:
                return {"date": raw[0], "label": raw[1], "color": raw[2]}
        return {"date": None, "label": str(raw), "event_id": f"event_{index:03d}"}

    @staticmethod
    def _raw_date(raw: Any) -> Any:
        return EventBeatBuilder._parse_raw_event(raw, 0).get("date")

    @staticmethod
    def _raw_label(raw: Any) -> Any:
        return EventBeatBuilder._parse_raw_event(raw, 0).get("label")

    @staticmethod
    def _extract_index(df: Any) -> List[Any]:
        if df is None:
            return []
        idx = getattr(df, "index", None)
        if idx is None and isinstance(df, dict):
            idx = df.get("index") or df.get("dates")
        if idx is None:
            return []
        try:
            return list(idx)
        except TypeError:
            return []

    @staticmethod
    def _to_date(value: Any) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if hasattr(value, "to_pydatetime"):
            try:
                return value.to_pydatetime().date()
            except Exception:
                pass
        if hasattr(value, "date") and callable(getattr(value, "date")):
            try:
                d = value.date()
                if isinstance(d, date):
                    return d
            except Exception:
                pass
        text = str(value).strip()
        if not text:
            return None
        if "T" in text:
            text = text.split("T", 1)[0]
        if " " in text:
            text = text.split(" ", 1)[0]
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(str(value)).date()
        except Exception:
            return None

    @staticmethod
    def _map_date(
        raw_date: Any,
        index_values: Sequence[Any],
        index_dates: Sequence[Optional[date]],
        tolerance_days: int = 3,
    ) -> Tuple[Any, Optional[int], Optional[str]]:
        target = EventBeatBuilder._to_date(raw_date)
        if target is None:
            return None, None, "invalid or missing event date"
        best_pos: Optional[int] = None
        best_delta: Optional[int] = None
        for pos, d in enumerate(index_dates):
            if d is None:
                continue
            delta = abs((d - target).days)
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_pos = pos
                if delta == 0:
                    break
        if best_pos is None or best_delta is None:
            return None, None, "no valid dates in df.index"
        if best_delta > tolerance_days:
            return None, None, f"date outside mapping tolerance ({best_delta} days > {tolerance_days})"
        return index_values[best_pos], best_pos, None

    @staticmethod
    def _coerce_event_type(value: Any) -> Optional[EventType]:
        if value is None:
            return None
        if isinstance(value, EventType):
            return value
        text = str(value).strip()
        if not text:
            return None
        try:
            return EventType(text)
        except ValueError:
            pass
        try:
            return EventType[text]
        except KeyError:
            return None

    @staticmethod
    def _style_for(event_type: EventType, color: Any = None) -> EventVisualStyle:
        base = STYLES.get(event_type, STYLES[EventType.default])
        if color:
            return replace(base, accent_color=str(color))
        return replace(base)

    @staticmethod
    def _normalize_ticker(value: Any, tickers: Any) -> Optional[str]:
        if value is None or value == "":
            return None
        ticker = str(value).upper().strip()
        if not ticker:
            return None
        try:
            known = {str(t).upper().strip() for t in tickers} if tickers is not None else set()
        except TypeError:
            known = set()
        return ticker if not known or ticker in known or ticker else None

    @staticmethod
    def _priority(scope: str, severity: str, parsed: Dict[str, Any]) -> int:
        if EventBeatBuilder._is_intlike(parsed.get("priority")):
            return int(parsed["priority"])
        if parsed.get("manual") is True:
            base = 0
        else:
            base = EventBeatBuilder.SCOPE_PRIORITY.get(str(scope), 5)
        return max(0, base + EventBeatBuilder.SEVERITY_BONUS.get(severity, 0))

    @staticmethod
    def _is_intlike(value: Any) -> bool:
        try:
            int(value)
            return value is not None and value != ""
        except Exception:
            return False

    @staticmethod
    def _apply_timing(beat: EventBeat, mapped_pos: Optional[int], index_len: int, video_plan: Any, fps: int) -> None:
        fps = int(fps or 30)
        fade_in = max(1, int(round(0.3 * fps)))
        hold_default = max(1, int(round(2.5 * fps)))
        fade_out = max(1, int(round(0.5 * fps)))
        hold = hold_default

        total_frames = EventBeatBuilder._get_attr(video_plan, "total_frames", None)
        if total_frames is None:
            duration = EventBeatBuilder._get_attr(video_plan, "duration", None) or EventBeatBuilder._get_attr(video_plan, "duration_seconds", None)
            if duration is not None:
                try:
                    total_frames = int(float(duration) * fps)
                except Exception:
                    total_frames = None
        if total_frames is None:
            total_frames = max(index_len * max(1, int(round(fps / 6))), fade_in + hold + fade_out + 1)

        plan_fps = EventBeatBuilder._get_attr(video_plan, "fps", None)
        if plan_fps:
            try:
                fps = int(plan_fps)
                fade_in = max(1, int(round(0.3 * fps)))
                hold = max(1, int(round(2.5 * fps)))
                fade_out = max(1, int(round(0.5 * fps)))
            except Exception:
                pass

        peak = EventBeatBuilder._frame_for_position(video_plan, mapped_pos, index_len, total_frames)
        beat.fade_in_frames = fade_in
        beat.hold_frames = hold
        beat.fade_out_frames = fade_out
        beat.peak_frame = peak
        beat.start_frame = max(0, peak - fade_in)
        beat.end_frame = min(int(total_frames), peak + hold + fade_out)
        beat.marker_only_after_end = beat.end_frame >= int(total_frames)

    @staticmethod
    def _frame_for_position(video_plan: Any, mapped_pos: Optional[int], index_len: int, total_frames: int) -> int:
        if mapped_pos is None:
            return 0
        frame_map = EventBeatBuilder._get_attr(video_plan, "date_to_frame", None)
        if isinstance(frame_map, dict):
            if mapped_pos in frame_map:
                try:
                    return int(frame_map[mapped_pos])
                except Exception:
                    pass
        if index_len <= 1:
            return 0
        return int(round((mapped_pos / float(index_len - 1)) * max(0, int(total_frames) - 1)))

    @staticmethod
    def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    @staticmethod
    def _index_position(value: Any, index_values: Sequence[Any]) -> Optional[int]:
        for i, candidate in enumerate(index_values):
            if candidate == value:
                return i
        value_date = EventBeatBuilder._to_date(value)
        if value_date is not None:
            for i, candidate in enumerate(index_values):
                if EventBeatBuilder._to_date(candidate) == value_date:
                    return i
        return None

    @staticmethod
    def _choose_winner(a: EventBeat, b: EventBeat) -> Tuple[EventBeat, EventBeat]:
        a_key = (a.priority, -EventBeatBuilder._severity_rank(a.severity), EventBeatBuilder._sortable_date(a.event_date_mapped))
        b_key = (b.priority, -EventBeatBuilder._severity_rank(b.severity), EventBeatBuilder._sortable_date(b.event_date_mapped))
        return (a, b) if a_key <= b_key else (b, a)

    @staticmethod
    def _severity_rank(severity: str) -> int:
        return {"low": 0, "medium": 1, "high": 2}.get(severity, 1)

    @staticmethod
    def _sortable_date(value: Any) -> date:
        return EventBeatBuilder._to_date(value) or date.max


class EventQA:
    """Structured QA checks for EventBeat collections.

    overlap window (final_hold_start_frame..endscreen_end_frame) is the HARD QA
    check mandated by SCENE_PLAN.md: "events duerfen sich nicht mit
    final_hold/endscreen-Phasen ueberlappen".
    """

    @staticmethod
    def run_qa(beats: Sequence[EventBeat], video_plan: Any = None) -> Dict[str, Any]:
        beats = list(beats or [])
        rendered = [b for b in beats if b.rendered and not b.skipped]
        skipped = [b for b in beats if b.skipped]
        marker_only = [b for b in beats if b.marker_only]
        deduped = [b for b in beats if b.skip_reason == "deduped within 40 data points" or b.collision_status == "deduped"]
        max_visible = EventBeatBuilder._get_attr(video_plan, "max_visible_events", 0) or 0
        try:
            max_visible = int(max_visible)
        except Exception:
            max_visible = 0

        final_hold_start = EventBeatBuilder._get_attr(video_plan, "final_hold_start_frame", None)
        final_hold_end = EventBeatBuilder._get_attr(video_plan, "final_hold_end_frame", None)
        crossfade_start = EventBeatBuilder._get_attr(video_plan, "crossfade_start_frame", None)
        crossfade_end = EventBeatBuilder._get_attr(video_plan, "crossfade_end_frame", None)
        # Brain's contract has no separate crossfade phase — endscreen overlap is
        # checked under the same field names the renderer-facing planning.py uses.
        endscreen_start = EventBeatBuilder._get_attr(video_plan, "endscreen_start_frame", None)
        endscreen_end = EventBeatBuilder._get_attr(video_plan, "endscreen_end_frame", None)

        labels_during_final_hold = EventQA._any_overlap(rendered, final_hold_start, final_hold_end)
        labels_during_crossfade = EventQA._any_overlap(rendered, crossfade_start, crossfade_end)
        labels_during_endscreen = EventQA._any_overlap(rendered, endscreen_start, endscreen_end)
        collisions_resolved = all(
            (b.collision_status in (None, "resolved", "deduped", "marker_only") or b.final_position is not None or b.marker_only or b.skipped)
            for b in beats
        )

        hard_fails: List[str] = []
        for b in skipped:
            if not b.skip_reason:
                hard_fails.append(f"{b.event_id}: skipped without skip_reason")
        if labels_during_final_hold:
            hard_fails.append("rendered event labels overlap final_hold")
        if labels_during_crossfade:
            hard_fails.append("rendered event labels overlap crossfade")
        if labels_during_endscreen:
            hard_fails.append("rendered event labels overlap endscreen")
        if not collisions_resolved:
            hard_fails.append("unresolved event collisions detected")

        per_event = []
        for b in beats:
            per_event.append({
                "event_id": b.event_id,
                "event_type": b.event_type.value if isinstance(b.event_type, EventType) else str(b.event_type),
                "ticker": b.ticker,
                "scope": b.scope,
                "date": str(b.event_date_mapped) if b.event_date_mapped is not None else None,
                "label_primary": b.label_primary,
                "label_secondary": b.label_secondary,
                "rendered": b.rendered,
                "skipped": b.skipped,
                "skip_reason": b.skip_reason,
                "marker_only": b.marker_only,
                "collision_status": b.collision_status,
                "start_frame": b.start_frame,
                "peak_frame": b.peak_frame,
                "end_frame": b.end_frame,
            })

        deduped_total = max(max([getattr(b, "_deduped_count_total", 0) for b in beats] or [0]), len(deduped))
        return {
            "event_count_total": len(beats),
            "event_count_rendered": len(rendered),
            "event_count_skipped": len(skipped),
            "event_count_marker_only": len(marker_only),
            "event_count_deduped": deduped_total,
            "max_visible_per_frame": max_visible,
            "event_labels_during_final_hold": labels_during_final_hold,
            "event_labels_during_crossfade": labels_during_crossfade,
            "event_labels_during_endscreen": labels_during_endscreen,
            "event_collisions_resolved": collisions_resolved,
            "hard_fails": hard_fails,
            "per_event": per_event,
        }

    @staticmethod
    def _any_overlap(beats: Sequence[EventBeat], start: Any, end: Any) -> bool:
        if start is None or end is None:
            return False
        try:
            s, e = int(start), int(end)
        except Exception:
            return False
        for b in beats:
            if b.label_primary or b.label_secondary:
                if b.start_frame <= e and b.end_frame >= s:
                    return True
        return False


__all__ = [
    "EventType", "EventVisualStyle", "EventBeat", "STYLES",
    "EventTextGenerator", "EventBeatBuilder", "EventQA",
]
