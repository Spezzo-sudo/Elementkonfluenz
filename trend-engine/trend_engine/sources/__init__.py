"""Trend source adapters for ValueRacer."""

from .base import TrendSignal, TrendSource
from .simulated import SimulatedTrendSource

__all__ = ["TrendSignal", "TrendSource", "SimulatedTrendSource"]
