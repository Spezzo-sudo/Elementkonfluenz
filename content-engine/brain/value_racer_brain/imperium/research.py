"""research.py — curated, sourced company-fact input model for the Imperium vertical.

Loaded from per-company YAML files (content-engine/brain/value_racer_brain/imperium/data/*.yaml).
Every numeric/historical claim carries an explicit source_url + source_date — there is no API
for "which brands does company X own", so this is the one input in the whole pipeline that is
written and checked by a human (or an AI assistant doing real web research), not computed.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

import yaml
from pydantic import BaseModel, ConfigDict

SCHEMA_VERSION = 1


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Owner(_Base):
    display_name: str
    legal_name: str
    hq_city: str
    founded_year: int
    ticker: str


class Brand(_Base):
    name: str
    category: str
    acquired_year: int
    color_primary: str = "#333333"
    color_text: str = "#FFFFFF"
    surprise_factor: int = 5  # 1 (well-known) .. 10 (surprising) — drives card ordering
    source_url: str
    source_date: date


class Fact(_Base):
    label: str  # e.g. "UMSATZ", "MITARBEITER", "PRAESENZ"
    value: float
    unit: str
    as_of_year: int
    description: str
    source_url: str
    source_date: date


class ScaleComparisonRow(_Base):
    label: str
    value: float
    source_url: str
    source_date: date


class ScaleComparison(_Base):
    headline: str
    unit: str
    rows: List[ScaleComparisonRow]  # rows[0] is the hero/owner company


class CompanyResearch(_Base):
    schema_version: int = SCHEMA_VERSION
    topic_id: str
    sector: str
    region: str
    owner: Owner
    brands: List[Brand]
    facts: List[Fact]
    scale_comparison: ScaleComparison
    researched_at: date
    verified: bool = False
    verified_at: Optional[date] = None
    verify_interval_days: int = 365

    @classmethod
    def from_yaml(cls, raw: str) -> "CompanyResearch":
        return cls.model_validate(yaml.safe_load(raw))
