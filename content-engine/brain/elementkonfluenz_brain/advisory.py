"""Advisory-wording compliance check — ported from VideoEngine._check_advisory_wording.

Flags titles that read like investment advice (German financial regulation
context: avoid wording implying a buy/sell recommendation or guaranteed return).
Keyword list and suggested rewordings kept verbatim from the source engine.
"""

from __future__ import annotations

from typing import Dict, List

# Verbatim from value_racer_video.py — compliance-sensitive, do not reword.
_RED_FLAG_KEYWORDS: List[str] = [
    "kaufen?", "verkaufen?", "all in", "sicherer gewinn", "garantiert",
    "muss man kaufen", "jetzt zugreifen", "verpassen", "kein risiko",
    "risikolos", "sicherer",
]

_SUGGESTIONS: List[str] = [
    "Was jetzt?", "Crash oder Chance?", "Rekordhoch - und jetzt?",
    "Rallye vorbei?", "Risiko oder Chance?", "Wer schlagt wen?",
]


def check_advisory_wording(title: str) -> Dict[str, object]:
    """Check a video title for investment-advice-like wording.

    Returns {"flagged": bool, "matched_keywords": [...], "warnings": [...], "suggestions": [...]}.
    """
    hook = title or ""
    matched: List[str] = []
    warnings: List[str] = []
    if hook:
        lowered = hook.lower()
        for w in _RED_FLAG_KEYWORDS:
            if w in lowered:
                matched.append(w)
                warnings.append(
                    f'Titel mit "{hook}" klingt nach Anlageberatung ("{w}"). Vorschlaege: {_SUGGESTIONS[:3]}'
                )

    return {
        "flagged": bool(matched),
        "matched_keywords": matched,
        "warnings": warnings,
        "suggestions": _SUGGESTIONS[:3] if matched else [],
    }
