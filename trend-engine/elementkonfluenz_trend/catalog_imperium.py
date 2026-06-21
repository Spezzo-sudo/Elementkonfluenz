"""Catalog B: imperium company candidates, tagged by sector/region for cooldown/rotation.

Starter catalog built from zero (no prior company research existed). Each entry is a
candidate for research, not yet a verified episode -- see content-engine Brain
`imperium/research.py` for the source-citation requirement before an episode is buildable.
"""
from .models import ImperiumTopic

CATALOG: list[ImperiumTopic] = [
    ImperiumTopic(
        topic_id="imperium_nestle",
        company_name="Nestlé S.A.",
        ticker="NESN.SW",
        sector="consumer_goods",
        region="EU",
        keywords=["nestle", "konzern", "marken"],
    ),
    ImperiumTopic(
        topic_id="imperium_mercedes",
        company_name="Mercedes-Benz Group AG",
        ticker="MBG.DE",
        sector="automotive",
        region="EU",
        keywords=["mercedes", "daimler", "autokonzern"],
    ),
    ImperiumTopic(
        topic_id="imperium_alphabet",
        company_name="Alphabet Inc.",
        ticker="GOOGL",
        sector="tech",
        region="US",
        keywords=["google", "alphabet", "tech-konzern"],
    ),
    ImperiumTopic(
        topic_id="imperium_jpmorgan",
        company_name="JPMorgan Chase & Co.",
        ticker="JPM",
        sector="finance",
        region="US",
        keywords=["jpmorgan", "bank", "finanzkonzern"],
    ),
    ImperiumTopic(
        topic_id="imperium_jnj",
        company_name="Johnson & Johnson",
        ticker="JNJ",
        sector="pharma",
        region="US",
        keywords=["pharma", "gesundheit", "konzern"],
    ),
    ImperiumTopic(
        topic_id="imperium_lvmh",
        company_name="LVMH Moët Hennessy Louis Vuitton",
        ticker="MC.PA",
        sector="luxury",
        region="EU",
        keywords=["luxus", "mode", "lvmh"],
    ),
    ImperiumTopic(
        topic_id="imperium_samsung",
        company_name="Samsung Electronics Co., Ltd.",
        ticker="005930.KS",
        sector="tech",
        region="APAC",
        keywords=["samsung", "elektronik", "koreakonzern"],
    ),
    ImperiumTopic(
        topic_id="imperium_toyota",
        company_name="Toyota Motor Corporation",
        ticker="7203.T",
        sector="automotive",
        region="APAC",
        keywords=["toyota", "autokonzern", "japan"],
    ),
]
