"""Hook-intro pool — visual variance for chart_race ScenePlan.hook_variant.

Each id maps 1:1 to an intro layout component in the renderer
(`renderer/src/components/IntroPhase.tsx`); the Brain only ever picks an id
string and never describes layout — that stays on the renderer side of the
Brain/Renderer boundary, same as everywhere else in this project.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional

HOOK_VARIANTS: Dict[str, Dict[str, str]] = {
    "default": {"id": "default"},
    "split_vs": {"id": "split_vs"},
    "stamp_cascade": {"id": "stamp_cascade"},
}

# Equal weights for now — same placeholder rationale as theme_pool.THEME_WEIGHTS.
HOOK_WEIGHTS: Dict[str, float] = {hook_id: 1.0 for hook_id in HOOK_VARIANTS}


def all_hook_variant_ids() -> List[str]:
    return list(HOOK_VARIANTS.keys())


def get_hook_variant_by_id(hook_variant_id: str) -> Dict[str, str]:
    if hook_variant_id not in HOOK_VARIANTS:
        raise KeyError(f"unknown hook_variant_id {hook_variant_id!r}; known ids: {sorted(HOOK_VARIANTS)}")
    return HOOK_VARIANTS[hook_variant_id]


def pick_hook_variant(rng: Optional[random.Random] = None) -> Dict[str, str]:
    rng = rng or random
    ids = list(HOOK_WEIGHTS.keys())
    weights = [HOOK_WEIGHTS[i] for i in ids]
    chosen = rng.choices(ids, weights=weights, k=1)[0]
    return HOOK_VARIANTS[chosen]
