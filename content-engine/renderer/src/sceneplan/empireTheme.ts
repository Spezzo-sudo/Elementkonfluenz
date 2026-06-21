/**
 * Presentation helpers for EmpireScenePlan's theme, which is deliberately
 * simpler than ScenePlan's (just id/accent_color/stamp_color — no
 * glow_mode/event_styles, since imperium has no live-data camera to style
 * per-volatility). Pure presentation, no decision logic.
 */

export function empireGlow(color: string): string {
  return `0 0 8px ${color}, 0 0 22px ${color}`;
}

export function empireBoxGlow(color: string): string {
  return `0 0 14px ${color}, 0 0 32px ${color}`;
}
