"""DataTimeMap — ported near-verbatim from value_racer_video.py.

Maps race_progress (0-1, position along the race-phase timeline) to
data_progress (0-1, position along the underlying data series) with an
early-cluster stretch so visually-bunched early data gets proportionally
more screen time before the assets diverge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


@dataclass
class DataTimeMap:
    """Maps race_progress (0-1) to data_progress (0-1) with cluster-stretch."""

    early_data_pct: float
    early_race_pct: float

    def __post_init__(self) -> None:
        self.early_data_pct = float(np.clip(self.early_data_pct, 0.0, 1.0))
        self.early_race_pct = float(np.clip(self.early_race_pct, 0.0, 1.0))
        if self.early_race_pct < self.early_data_pct:
            self.early_race_pct = self.early_data_pct
        if self.early_race_pct >= 1.0 and self.early_data_pct < 1.0:
            self.early_race_pct = 1.0 - 1e-12

    @staticmethod
    def _smoothstep(t: float) -> float:
        t = float(np.clip(t, 0.0, 1.0))
        return t * t * (3.0 - 2.0 * t)

    def map(self, race_progress: float) -> float:
        """Piecewise monotone smoothstep mapping without overshoot."""
        rp = float(np.clip(race_progress, 0.0, 1.0))
        ed = float(np.clip(self.early_data_pct, 0.0, 1.0))
        er = float(np.clip(self.early_race_pct, 0.0, 1.0))
        if er <= 0.0 or ed <= 0.0:
            return rp
        if er >= 1.0:
            return float(np.clip(ed * self._smoothstep(rp), 0.0, 1.0))
        if rp <= er:
            t = rp / er
            out = ed * self._smoothstep(t)
        else:
            t = (rp - er) / max(1e-12, 1.0 - er)
            out = ed + (1.0 - ed) * self._smoothstep(t)
        return float(np.clip(out, 0.0, 1.0))

    def inverse(self, data_progress: float, tolerance: float = 1e-6, max_iter: int = 50) -> float:
        """Binary-search inverse: find race_progress such that map(rp) ~= data_progress.
        Guarantees data_progress=0->0, data_progress=1->1, monotone, no overshoot."""
        dp = float(np.clip(data_progress, 0.0, 1.0))
        if dp <= 0.0:
            return 0.0
        if dp >= 1.0:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(max_iter):
            mid = (lo + hi) * 0.5
            val = self.map(mid)
            if abs(val - dp) < tolerance:
                return mid
            if val < dp:
                lo = mid
            else:
                hi = mid
        return (lo + hi) * 0.5


def _safe_cluster_rows(df: pd.DataFrame) -> pd.DataFrame:
    if hasattr(df, "select_dtypes"):
        numeric = df.select_dtypes(include=[np.number])
    else:
        numeric = pd.DataFrame(df)
    return numeric.replace([np.inf, -np.inf], np.nan).dropna(how="all")


def analyze_early_cluster(df: pd.DataFrame) -> dict:
    """Analyze the early line cluster and derive a TimeMap base.

    cluster_threshold of 0.10 (<=4 assets) / 0.15 (5+) and the divergence "required_run"
    window (>=3 points, >=3% of series length) were tuned in the source engine to avoid
    flagging single-day noise as a real divergence — kept verbatim.
    """
    numeric = _safe_cluster_rows(df)
    asset_count = int(len(numeric.columns)) if numeric is not None else 0
    cluster_threshold = 0.10 if asset_count <= 4 else 0.15
    if numeric is None or numeric.empty or asset_count == 0:
        return {
            "asset_count": asset_count, "cluster_threshold": cluster_threshold,
            "divergence_idx": None, "divergence_date": None,
            "early_data_pct": 0.10, "early_cluster_score": 0.0, "spread_series": [],
        }

    spreads = []
    for _, row in numeric.iterrows():
        vals = row.dropna().astype(float).values
        if len(vals) == 0:
            spreads.append(0.0)
            continue
        denom = float(np.nanmedian(vals))
        if not np.isfinite(denom) or abs(denom) < 1e-12:
            denom = float(np.nanmean(vals))
        if not np.isfinite(denom) or abs(denom) < 1e-12:
            spreads.append(0.0)
            continue
        spreads.append(float(max(0.0, (np.nanmax(vals) - np.nanmin(vals)) / abs(denom))))

    spread_series = pd.Series(spreads, index=numeric.index, dtype=float).fillna(0.0)
    required_run = max(3, int(len(numeric) * 0.03))
    divergence_idx = None
    above = (spread_series > cluster_threshold).tolist()
    for i in range(0, len(above) - required_run + 1):
        if all(above[i:i + required_run]):
            divergence_idx = i
            break

    default_early = 0.25
    if divergence_idx is None:
        early_raw = min(0.15 * len(numeric), default_early)
    else:
        early_raw = divergence_idx / max(1, len(numeric) - 1)
    early_data_pct = float(np.clip(early_raw, 0.05, 0.25))

    cluster_end = max(1, int(round(early_data_pct * len(numeric)))) if divergence_idx is None else max(1, divergence_idx)
    cluster_spread = float(spread_series.iloc[:cluster_end].mean()) if len(spread_series) else 0.0

    pct = numeric.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.0)
    window = 20 if len(numeric) >= 20 else min(10, max(2, len(numeric)))
    movement_pct = pd.Series(0.0, index=numeric.index, dtype=float)
    if window >= 2 and len(numeric) >= 2:
        roll_max = numeric.rolling(window, min_periods=2).max()
        roll_min = numeric.rolling(window, min_periods=2).min()
        start_values = numeric.shift(window - 1).abs().replace(0, np.nan)
        movement_df = ((roll_max - roll_min) / start_values).replace([np.inf, -np.inf], np.nan)
        movement_pct = movement_df.mean(axis=1).fillna(pct.abs().mean(axis=1).fillna(0.0))
    early_volatility = float(np.clip(
        movement_pct.iloc[:cluster_end].mean() if len(movement_pct) else 0.0, 0.0, 1.0,
    ))

    asset_factor = float(np.clip(asset_count / 8.0, 0.0, 1.0))
    duration_factor = float(np.clip(early_data_pct / 0.25, 0.0, 1.0))
    tight_factor = float(1.0 - np.clip(cluster_spread, 0.0, 1.0))
    volatility_factor = float(np.clip(early_volatility / 0.10, 0.0, 1.0))
    score = asset_factor * 0.25 + duration_factor * 0.25 + tight_factor * 0.30 + volatility_factor * 0.20
    early_cluster_score = float(np.clip(score, 0.0, 1.0))

    divergence_date = None
    if divergence_idx is not None and divergence_idx < len(numeric.index):
        _d = numeric.index[divergence_idx]
        divergence_date = str(_d.date() if hasattr(_d, "date") else _d)

    return {
        "asset_count": asset_count, "cluster_threshold": cluster_threshold,
        "divergence_idx": divergence_idx, "divergence_date": divergence_date,
        "early_data_pct": early_data_pct, "early_cluster_score": early_cluster_score,
        "early_volatility": early_volatility,
        "spread_series": [float(x) for x in spread_series.tolist()],
    }


def score_to_time_map(score: float, early_data_pct: float, early_volatility: float = 0.0) -> DataTimeMap:
    score = float(np.clip(score, 0.0, 1.0))
    early_data_pct = float(np.clip(early_data_pct, 0.05, 0.25))
    if score < 0.3:
        early_race_pct = early_data_pct * 1.1
    elif score < 0.6:
        early_race_pct = early_data_pct * 1.8
    else:
        early_race_pct = early_data_pct * 2.3
    early_race_pct = min(early_race_pct, 0.30)
    early_race_pct = max(early_race_pct, early_data_pct)
    # Cap stretch for very early divergence (early_data_pct<=0.07 means barely any
    # cluster to begin with, so a big stretch would distort more than it helps).
    if early_data_pct <= 0.07:
        max_early_race = 0.10
        max_stretch = 1.5
        early_vol = float(np.clip(early_volatility, 0.0, 1.0))
        if early_vol > 0.15:
            max_early_race = 0.12
            max_stretch = 2.0
        early_race_pct = min(early_race_pct, early_data_pct * max_stretch)
        early_race_pct = min(early_race_pct, max_early_race)
        early_race_pct = max(early_race_pct, early_data_pct)
    return DataTimeMap(early_data_pct, early_race_pct)


def build_control_points(
    time_map: DataTimeMap, race_start_frame: int, race_end_frame: int, n_points: int = 21
) -> list[dict]:
    """Sample the DataTimeMap into {frame, data_index} control points for the
    renderer to interpolate between (avoids re-deriving the smoothstep curve
    client-side, per the "frames are the only time unit" invariant)."""
    span = max(1, race_end_frame - race_start_frame)
    points = []
    for i in range(n_points):
        race_progress = i / max(1, n_points - 1)
        frame = race_start_frame + int(round(race_progress * span))
        data_index = time_map.map(race_progress)
        points.append({"frame": frame, "data_index": round(data_index, 6)})
    return points


def _stable_ranking(
    tickers: Sequence[str],
    values: Dict[str, Optional[float]],
    prev_ranking: Optional[List[str]] = None,
    last_valid_values: Optional[Dict[str, float]] = None,
    threshold: float = 0.003,
) -> Tuple[List[str], Dict[str, float]]:
    """Sort tickers with hysteresis + NaN stability + single-pass swap.

    Pure-function port of VideoEngine._stable_ranking. The original mutated
    `self._prev_ranking` / `self._last_valid_values` as instance state across
    frames; here the caller owns that state explicitly and threads both the
    new ranking and the updated `last_valid_values` into the next call (once
    per leaderboard frame the Brain needs to plan ranking transitions for).

    NaN tickers keep their last known value (degressive x0.999) so they do NOT
    disappear from the ranking. Single-pass: max 1 position swap per ticker
    per call, for smooth animation.
    """
    last_valid_values = dict(last_valid_values or {})
    clean_values: Dict[str, float] = {}
    for t in tickers:
        v = values.get(t)
        if v is None or (isinstance(v, float) and np.isnan(v)):
            if t in last_valid_values:
                clean_values[t] = last_valid_values[t] * 0.999
            else:
                clean_values[t] = 0.0
        else:
            if isinstance(v, (int, float)) and v > 0:
                last_valid_values[t] = v
            clean_values[t] = v

    if not prev_ranking:
        ranking = sorted(tickers, key=lambda t: clean_values.get(t, 0), reverse=True)
        return ranking, last_valid_values

    # Order preserving: keep old order
    ranking = [t for t in prev_ranking if t in tickers]
    for t in tickers:
        if t not in ranking:
            ranking.append(t)

    # Single-pass bubble sort: each ticker max 1 position per call
    swapped = set()
    for i in range(len(ranking) - 1):
        a, b = ranking[i], ranking[i + 1]
        if a in swapped or b in swapped:
            continue
        va = clean_values.get(a, 0)
        vb = clean_values.get(b, 0)
        if vb > va * (1 + threshold):
            ranking[i], ranking[i + 1] = b, a
            swapped.add(a)
            swapped.add(b)

    return ranking, last_valid_values
