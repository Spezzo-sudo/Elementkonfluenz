"""value_racer_brain.imperium — Brain subpackage for the "Imperium" content vertical.

Produces a versioned EmpireScenePlan JSON document from curated, sourced company
research (see research.py). Unlike the chart_race ast, brand/fact data is not
fetched from any API — there is none for "which brands does company X own" — so
this subpackage's one non-deterministic input is the YAML files under data/,
written and source-checked by a human (or an AI assistant doing real research).
"""

from .builder import build_empire_scene_plan
from .research import CompanyResearch
from .scene_plan import EmpireScenePlan

__all__ = ["build_empire_scene_plan", "CompanyResearch", "EmpireScenePlan"]
