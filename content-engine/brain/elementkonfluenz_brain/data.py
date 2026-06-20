"""Data loading and validation — ported from value_racer_video.py.

Pure pandas/numpy/yfinance. No matplotlib, no PIL, no class/`self` coupling:
every VideoEngine method here is rewritten as a plain function taking explicit
arguments so the Brain can run headless and be unit tested without a class.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class DataError(Exception):
    """Raised when usable price data could not be assembled for any ticker."""


# Ticker -> display name overrides. TICKER_OVERRIDES takes precedence over
# yfinance info lookups (verbatim from value_racer_video.py, trimmed to the
# entries actually needed; unknown tickers fall back to yfinance info / raw ticker).
TICKER_OVERRIDES: Dict[str, str] = {
    "AAPL": "Apple", "ABNB": "Airbnb", "ADA-USD": "Cardano", "ADBE": "Adobe",
    "AMD": "AMD", "AMGN": "Amgen", "AMZN": "Amazon", "ARM": "ARM Holdings",
    "ASML": "ASML", "AVGO": "Broadcom", "BA": "Boeing", "BABA": "Alibaba",
    "BAC": "Bank of America", "BRK.A": "Berkshire", "BRK.B": "Berkshire",
    "BTC-USD": "Bitcoin", "COIN": "Coinbase", "COST": "Costco",
    "CVX": "Chevron", "DIA": "Dow Jones", "DUOL": "Duolingo",
    "ETH-USD": "Ethereum", "GC=F": "Gold", "GLD": "Gold",
    "^GSPC": "S&P 500", "^DJI": "Dow Jones", "^IXIC": "Nasdaq",
    "^GDAXI": "DAX", "SPY": "S&P 500", "QQQ": "Nasdaq 100",
}


def format_ticker_label(ticker: str, info: Optional[dict] = None) -> str:
    """Build display label 'Kurzname (TICKER)'. TICKER_OVERRIDES wins over yfinance info."""
    override = TICKER_OVERRIDES.get(ticker)
    if override:
        if override.upper() == ticker.upper():
            return ticker
        return f"{override} ({ticker})"

    if info is None:
        info = {}
    name = (
        info.get("shortName")
        or (info.get("longName", "").split()[0] if info.get("longName") else None)
        or ticker
    )
    if len(name) > 16:
        name = name[:15] + "…"
    if name.upper() == ticker.upper():
        return ticker
    return f"{name} ({ticker})"


def calculate_dca(prices_series: pd.Series, monthly_rate: float, day_of_month: int = 1) -> pd.Series:
    """DCA curve: monthly_rate is invested on day_of_month every month, starting with monthly_rate."""
    shares = 0.0
    values = []
    prev_month = None
    dates = prices_series.index
    for i in range(len(prices_series)):
        date = dates[i]
        price = prices_series.iloc[i]
        if i == 0:
            shares = monthly_rate / price
        else:
            if date.month != prev_month and date.day >= day_of_month:
                shares += monthly_rate / price
        prev_month = date.month
        values.append(shares * price)
    return pd.Series(values, index=prices_series.index)


def _normalize_tz(ts_or_series):
    """Strip timezone info from a Timestamp or DataFrame/Series index."""
    if hasattr(ts_or_series, "index") and ts_or_series.index is not None:
        if hasattr(ts_or_series.index, "tz") and ts_or_series.index.tz is not None:
            ts_or_series.index = ts_or_series.index.tz_localize(None)
    elif hasattr(ts_or_series, "tz") and ts_or_series.tz is not None:
        return ts_or_series.tz_localize(None)
    return ts_or_series


def validate_data(df: pd.DataFrame) -> Dict[str, dict]:
    """Plausibility-check loaded data. Returns {ticker: {valid, issues, score, data_points, missing_pct}}."""
    checks: Dict[str, dict] = {}
    for ticker in df.columns:
        series = df[ticker].dropna()
        issues: List[str] = []
        if len(series) < 10:
            issues.append(f"Nur {len(series)} Datenpunkte")
        missing = df[ticker].isna().sum()
        total = len(df[ticker])
        if total > 0 and missing / total > 0.5:
            issues.append(f"{missing / total * 100:.0f}% fehlende Daten")
        daily_returns = series.pct_change().dropna()
        if len(daily_returns) > 0 and (daily_returns.abs() > 0.5).any():
            issues.append(">50% Tages-Return (Split?)")
        if len(daily_returns) > 20:
            _med = daily_returns.median()
            _mad = (daily_returns - _med).abs().median() * 1.4826
            _threshold = max(0.10, _mad * 5)
            _outliers = daily_returns[abs(daily_returns - _med) > _threshold]
            if len(_outliers) > max(3, len(daily_returns) * 0.02):
                issues.append(f"{len(_outliers)} Ausreisser (MAD>{_threshold:.2f})")
            if len(daily_returns) > 5 and (daily_returns.abs() > 0.35).sum() > 1:
                issues.append("Mehrere >35% Spikes")
        final_val = series.iloc[-1] if len(series) > 0 else 0
        if final_val < 1:
            issues.append(f"Endwert ${final_val:.2f} < $1 (Delisting?)")
        score = max(0, 100 - len(issues) * 20)
        checks[ticker] = {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": score,
            "data_points": len(series),
            "missing_pct": missing / total * 100 if total > 0 else 0,
        }
    return checks


@dataclass
class AssetStats:
    cagr: float = 0.0
    max_dd: float = 0.0
    final_value: float = 0.0


@dataclass
class DownloadResult:
    df: pd.DataFrame
    div_data: Dict[str, pd.Series] = field(default_factory=dict)
    savings_data: Dict[str, pd.Series] = field(default_factory=dict)
    validation_results: Dict[str, dict] = field(default_factory=dict)
    stats: Dict[str, AssetStats] = field(default_factory=dict)
    winner: Optional[str] = None


def _validate_dates(df: pd.DataFrame, start_date) -> pd.DataFrame:
    """Trim to the latest date at which ALL assets have a value (latest IPO)."""
    if df is None or df.empty:
        return df
    original_start = pd.Timestamp(start_date)
    first_valid = df.dropna(how="any")
    if len(first_valid) > 0:
        latest_start = first_valid.index[0]
        if latest_start > original_start:
            trimmed = df[df.index >= latest_start]
            if len(trimmed) > 10:
                logger.info("Start auf %s korrigiert (spaetestes IPO)", latest_start.date())
                return trimmed
            logger.warning("Zu wenige Daten nach Trim (%d), behalte Original", len(trimmed))
    return df


def download_data_sync(
    tickers: List[str],
    start_date,
    end_date,
    investment: float = 1000.0,
    mode: str = "evergreen",
    show_savings_plan: bool = False,
    monthly_rate: float = 100.0,
) -> DownloadResult:
    """Download price data via yfinance, normalize, validate, drop bad tickers, compute stats.

    mode="news" normalizes to percent growth from 0%; otherwise to absolute USD
    from `investment`. No class-level cache here (Brain runs are one-shot CLI calls).
    """
    data: Dict[str, pd.Series] = {}
    savings_data: Dict[str, pd.Series] = {}
    div_data: Dict[str, pd.Series] = {}
    validation_results: Dict[str, dict] = {}

    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
            if df.empty:
                logger.warning("Keine Kursdaten fuer %s (delisted? Zeitraum pruefen)", ticker)
                validation_results[ticker] = {"valid": False, "error": "no_data"}
                continue

            if "Close" in df.columns:
                prices = df["Close"].iloc[:, 0] if isinstance(df.columns, pd.MultiIndex) else df["Close"]
            elif "Adj Close" in df.columns:
                prices = df["Adj Close"].iloc[:, 0] if isinstance(df.columns, pd.MultiIndex) else df["Adj Close"]
            else:
                prices = df.iloc[:, 0]

            prices = prices.dropna()
            if len(prices) < 10:
                validation_results[ticker] = {"valid": False, "error": "insufficient_data"}
                continue

            data[ticker] = prices

            try:
                tk = yf.Ticker(ticker)
                div = tk.dividends
                if div is not None and len(div) > 0:
                    div_series = div.loc[div.index >= pd.Timestamp(start_date)]
                    if len(div_series) > 0:
                        div_data[ticker] = div_series.reindex(prices.index, method="ffill").fillna(0).cumsum()
            except Exception:
                pass

            if show_savings_plan:
                savings_data[ticker] = calculate_dca(prices, monthly_rate)

        except Exception as e:  # noqa: BLE001 - yfinance raises assorted exceptions across versions
            logger.error("Fehler beim Download von %s: %s", ticker, e)
            validation_results[ticker] = {"valid": False, "error": str(e)}
            continue

    if not data:
        raise DataError("Keine Kursdaten herunterladbar")

    df_all = pd.DataFrame(data).dropna(axis=0, how="all")
    df_all = _normalize_tz(df_all)

    for col in df_all.columns:
        start_idx = df_all[col].first_valid_index()
        if start_idx is not None:
            start_price = df_all[col].loc[start_idx]
            if start_price > 0:
                if mode == "news":
                    df_all[col] = (df_all[col] / start_price - 1) * 100
                else:
                    df_all[col] = df_all[col] / start_price * investment

    for t in list(div_data.keys()):
        if t in data and len(data[t]) > 0:
            start_p = data[t].dropna().iloc[0]
            if start_p > 0:
                div_data[t] = div_data[t] / start_p * investment

    if show_savings_plan:
        for t in list(savings_data.keys()):
            if t in data and len(data[t]) > 0:
                start_p = data[t].dropna().iloc[0]
                if start_p > 0:
                    savings_data[t] = savings_data[t] / start_p * investment

    # Normalize first, THEN trim to the common start (latest IPO across assets).
    df_all = _validate_dates(df_all, start_date)

    if show_savings_plan:
        for t in list(savings_data.keys()):
            savings_data[t] = savings_data[t].reindex(df_all.index).interpolate(limit=5).ffill()
    if div_data:
        for t in list(div_data.keys()):
            div_data[t] = div_data[t].reindex(df_all.index).interpolate(limit=5).ffill().fillna(0)

    # Re-normalize after trim so every asset starts at `investment` on the common start date.
    for col in df_all.columns:
        first_valid = df_all[col].dropna()
        if len(first_valid) > 0:
            start_price = first_valid.iloc[0]
            if start_price > 0:
                df_all[col] = df_all[col] / start_price * investment

    validation_results = validate_data(df_all)

    bad = [t for t, c in validation_results.items() if not c.get("valid", True)]
    if bad:
        logger.warning("Entferne ungueltige Ticker: %s", bad)
        for t in bad:
            if t in df_all.columns:
                del df_all[t]
            div_data.pop(t, None)
            savings_data.pop(t, None)
        if df_all.empty or len(df_all.columns) < 2:
            detail = "; ".join(f"{t}: {', '.join(validation_results[t]['issues'][:3])}" for t in bad)
            raise DataError(
                f"Nach Filterung nur {len(df_all.columns)} Ticker uebrig (benoetigt >=2). Entfernt: {detail}"
            )
        validation_results = validate_data(df_all)

    stats, winner = _calc_stats(df_all, investment)
    return DownloadResult(
        df=df_all,
        div_data=div_data,
        savings_data=savings_data,
        validation_results=validation_results,
        stats=stats,
        winner=winner,
    )


def _calc_stats(df: pd.DataFrame, investment: float) -> tuple[Dict[str, AssetStats], Optional[str]]:
    """CAGR, MaxDD, and final values per ticker. Returns (stats, winner_ticker)."""
    stats: Dict[str, AssetStats] = {}
    if df is None or df.empty:
        return stats, None
    for ticker in df.columns:
        series = df[ticker].dropna()
        if len(series) < 2:
            continue
        years = (series.index[-1] - series.index[0]).days / 365.25
        cagr = (series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1 if years > 0 else 0.0
        rolling_max = series.expanding().max()
        dd = (series - rolling_max) / rolling_max
        stats[ticker] = AssetStats(
            cagr=float(cagr),
            max_dd=float(dd.min()),
            final_value=float(investment * (series.iloc[-1] / series.iloc[0])),
        )
    winner = max(stats, key=lambda t: stats[t].final_value) if stats else None
    return stats, winner
