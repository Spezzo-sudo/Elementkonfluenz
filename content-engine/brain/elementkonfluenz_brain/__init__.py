"""elementkonfluenz_brain — pure-logic Brain for the asset-race video pipeline.

Produces a versioned ScenePlan JSON document. Contains no matplotlib/PIL/ffmpeg
and performs no pixel rendering; see content-engine/SCENE_PLAN.md for the contract.
"""

from .scene_plan import ScenePlan

__all__ = ["ScenePlan"]
