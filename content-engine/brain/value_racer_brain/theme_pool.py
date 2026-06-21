"""Theme pool — visual variance for chart_race ScenePlan.theme.

Multiple Theme dicts (matching the Theme/ThemeColors shape in scene_plan.py)
plus weighted random selection, so consecutive ScenePlans don't all render
with the same single visual identity (Phase 2 of the project plan: combat
algorithmic "templated content" detection by varying the first seconds of
each video).

`event_styles` is identical across all themes on purpose: those colors are
semantic (gain/loss/crash/ATH), not stylistic — varying them by theme would
make events harder to read consistently from video to video.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

from . import events as events_mod


def _event_styles() -> Dict[str, Any]:
    return {
        et.value: {"color": style.accent_color, "pulse": style.pulse}
        for et, style in events_mod.STYLES.items()
    }


def _theme(
    theme_id: str,
    bg: Tuple[str, str],
    text: Tuple[str, str],
    accent: str,
    font_family: str,
    glow_mode: str,
) -> Dict[str, Any]:
    return {
        "id": theme_id,
        "colors": {
            "bg": {"primary": bg[0], "secondary": bg[1]},
            "text": {"primary": text[0], "secondary": text[1]},
            "accent": {"primary": accent},
        },
        "font_family": font_family,
        "glow_mode": glow_mode,
        "event_styles": _event_styles(),
    }


# Font families are kept to generic, locally-available CSS stacks (no
# @font-face/web-font loading exists in the renderer yet) so each theme still
# renders with a visibly different typeface in headless Chromium without
# adding a new font-loading dependency.
THEMES: Dict[str, Dict[str, Any]] = {
    "default_dark": _theme(
        "default_dark",
        bg=("#080c14", "#0f1623"),
        text=("#FFFFFF", "#AAAAAA"),
        accent="#00E5FF",
        font_family="Inter",
        glow_mode="full",
    ),
    "neon_sunset": _theme(
        "neon_sunset",
        bg=("#1a0a08", "#2b1410"),
        text=("#FFF5E6", "#FFC299"),
        accent="#FF6B35",
        font_family="Verdana, Geneva, sans-serif",
        glow_mode="full",
    ),
    "mint_fresh": _theme(
        "mint_fresh",
        bg=("#0a1f1a", "#0f2922"),
        text=("#E8FFF7", "#9FFFE0"),
        accent="#2DD4BF",
        font_family="Georgia, 'Times New Roman', serif",
        glow_mode="subtle",
    ),
    "crimson_pulse": _theme(
        "crimson_pulse",
        bg=("#1a0505", "#260808"),
        text=("#FFE5E5", "#FF9999"),
        accent="#DC2626",
        font_family="'Courier New', monospace",
        glow_mode="full",
    ),
}

# Equal weights for now — placeholder until the analytics-engine feedback loop
# (Phase 4 of the project plan) replaces these with performance-derived values.
THEME_WEIGHTS: Dict[str, float] = {theme_id: 1.0 for theme_id in THEMES}


def all_theme_ids() -> List[str]:
    return list(THEMES.keys())


def get_theme_by_id(theme_id: str) -> Dict[str, Any]:
    if theme_id not in THEMES:
        raise KeyError(f"unknown theme_id {theme_id!r}; known ids: {sorted(THEMES)}")
    return THEMES[theme_id]


def pick_theme(rng: Optional[random.Random] = None) -> Dict[str, Any]:
    rng = rng or random
    ids = list(THEME_WEIGHTS.keys())
    weights = [THEME_WEIGHTS[i] for i in ids]
    chosen = rng.choices(ids, weights=weights, k=1)[0]
    return THEMES[chosen]
