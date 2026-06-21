"""Pydantic models for the TopicBrief contract (trend-engine -> content-engine).

See TOPIC_BRIEF.md for the JSON shape this mirrors.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

SCHEMA_VERSION = 1

ContentType = Literal["chart_race", "imperium"]

AssetCategory = Literal[
    "crypto_major",
    "crypto_alt",
    "single_stock",
    "index_etf",
    "commodity",
    "mixed_basket",
]

Sector = Literal[
    "consumer_goods",
    "automotive",
    "tech",
    "finance",
    "pharma",
    "luxury",
    "retail",
    "energy",
    "media",
]

Region = Literal["EU", "US", "APAC", "LATAM", "MEA"]


class ChartRaceTopic(BaseModel):
    topic_id: str
    tickers: List[str]
    category: AssetCategory
    period_days: int
    keywords: List[str] = Field(default_factory=list)


class ImperiumTopic(BaseModel):
    topic_id: str
    company_name: str
    ticker: Optional[str] = None
    sector: Sector
    region: Region
    keywords: List[str] = Field(default_factory=list)


class TopicBrief(BaseModel):
    schema_version: int = SCHEMA_VERSION
    content_type: ContentType
    selected_at: datetime
    trend_score: float
    reason: str
    chart_race: Optional[ChartRaceTopic] = None
    imperium: Optional[ImperiumTopic] = None
