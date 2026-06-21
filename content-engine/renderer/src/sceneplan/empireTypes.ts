/**
 * TypeScript mirror of the EmpireScenePlan contract defined in
 * `content-engine/EMPIRE_SCENE_PLAN.md`.
 *
 * Field names intentionally stay snake_case to match the JSON emitted by
 * the Python "Brain" (value_racer_brain.imperium) verbatim — same rule as
 * sceneplan/types.ts for the chart_race ScenePlan. The renderer must not
 * contain business/decision logic; these types only describe shape.
 */

export interface EmpireTopic {
  topic_id: string;
  company_name: string;
  ticker: string;
  sector: string;
  region: string;
}

export interface EmpirePhaseRange {
  start_frame: number;
  end_frame: number;
}

export interface EmpireDuration {
  total_frames: number;
  total_duration_sec: number;
  phases: {
    hook: EmpirePhaseRange;
    register_cards: EmpirePhaseRange;
    beat: EmpirePhaseRange;
    stamp: EmpirePhaseRange;
    facts: EmpirePhaseRange;
    scale: EmpirePhaseRange;
    endcard: EmpirePhaseRange;
  };
}

export interface EmpireOwner {
  display_name: string;
  legal_name: string;
  hq_city: string;
  founded_year: number;
}

export interface BrandCard {
  name: string;
  category: string;
  year: number;
  color: string;
  text_color: string;
}

export interface FactCard {
  label: string;
  display_value: string;
  unit: string;
  year: number;
  description: string;
}

export interface ScaleComparisonRow {
  label: string;
  value: number;
  hero: boolean;
}

export interface ScaleComparison {
  headline: string;
  unit: string;
  rows: ScaleComparisonRow[];
}

export interface EmpireEndcard {
  ticker_label: string;
  stock_from: number;
  stock_to: number;
  gain_pct: number;
  disclaimer: string;
}

export interface EmpireTheme {
  id: string;
  accent_color: string;
  stamp_color: string;
}

export interface EmpireQAResult {
  check: string;
  passed: boolean;
  detail: string;
}

export interface EmpireQA {
  hard_fail: boolean;
  sources_verified: boolean;
  results: EmpireQAResult[];
}

export interface EmpireScenePlan {
  schema_version: 1;
  video_id: string;
  topic: EmpireTopic;
  fps: number;
  duration: EmpireDuration;
  owner: EmpireOwner;
  hook_lines: string[];
  beat_line: string;
  brands: BrandCard[];
  facts: FactCard[];
  scale_comparison: ScaleComparison;
  endcard: EmpireEndcard;
  theme: EmpireTheme;
  qa: EmpireQA;
}

/**
 * Props passed into <EmpireScenePlanComposition>. Same deep-merge reasoning
 * as ScenePlanCompositionProps: the Brain CLI writes EmpireScenePlan to disk
 * with no wrapper key, so `--props=empire_scene_plan.json` must land directly
 * on these fields.
 */
export interface EmpireScenePlanCompositionProps extends EmpireScenePlan {
  [key: string]: unknown;
}
