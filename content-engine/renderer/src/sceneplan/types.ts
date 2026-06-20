/**
 * TypeScript mirror of the ScenePlan contract defined in
 * `content-engine/SCENE_PLAN.md`.
 *
 * IMPORTANT: Field names intentionally stay snake_case to match the JSON
 * emitted by the Python "Brain" verbatim. Do NOT camelCase these — the
 * renderer must consume the contract as-is, with zero translation layer
 * that could silently diverge from the Brain's schema.
 *
 * The renderer must not contain business/decision logic. These types exist
 * purely to describe the shape of data the renderer paints.
 */

export type CameraPolicy = 'stock_value' | 'percent' | 'high_volatility';

export type GlowMode = 'full' | 'subtle' | 'reduced' | 'minimal';

export type EventType =
  | 'crash'
  | 'ath_record'
  | 'geopolitical_risk'
  | 'energy_shock'
  | 'financial_crisis'
  | 'macro_rate'
  | 'earnings'
  | 'default';

export interface ScenePlanTopic {
  assets: string[];
  period_days: number;
  locale: string;
}

export interface PhaseRange {
  start_frame: number;
  end_frame: number;
}

export interface ScenePlanDuration {
  total_frames: number;
  total_duration_sec: number;
  phases: {
    intro: PhaseRange;
    race: PhaseRange;
    final_hold: PhaseRange;
    endscreen: PhaseRange;
  };
}

export interface DataSeries {
  ticker: string;
  label: string;
  color: string;
  dates: string[];
  /** Values may contain non-numeric placeholders in malformed input; renderer must not crash on these. */
  values: Array<number | string>;
}

export interface CameraKeyframe {
  frame: number;
  x_min: number;
  x_max: number;
  y_min: number;
  y_max: number;
}

export interface ScenePlanCamera {
  policy: CameraPolicy;
  keyframes: CameraKeyframe[];
}

export interface TimeMapControlPoint {
  frame: number;
  data_index: number;
}

export interface ScenePlanTimeMap {
  enabled: boolean;
  control_points: TimeMapControlPoint[];
}

export interface ScenePlanEvent {
  frame_start: number;
  frame_end: number;
  ticker: string;
  type: EventType;
  /** <= 42 chars per contract. */
  label: string;
  style_ref: string;
}

export interface EventStyle {
  color: string;
  pulse: boolean;
}

export interface ThemeColors {
  bg: Record<string, string>;
  text: Record<string, string>;
  accent: Record<string, string>;
}

export interface ScenePlanTheme {
  id: string;
  colors: ThemeColors;
  font_family: string;
  glow_mode: GlowMode;
  event_styles: Record<string, EventStyle>;
}

export interface HookVariant {
  id: string;
}

export interface EndscreenFinalValue {
  ticker: string;
  value: number;
  gain_pct: number;
}

export interface ScenePlanEndscreen {
  final_values: EndscreenFinalValue[];
  thumbnail_source_frame: number;
}

export interface QAResult {
  check: string;
  passed: boolean;
  detail: string;
}

export interface ScenePlanQA {
  hard_fail: boolean;
  results: QAResult[];
}

export interface ScenePlan {
  schema_version: 1;
  video_id: string;
  topic: ScenePlanTopic;
  fps: number;
  duration: ScenePlanDuration;
  data_series: DataSeries[];
  camera: ScenePlanCamera;
  time_map: ScenePlanTimeMap;
  events: ScenePlanEvent[];
  theme: ScenePlanTheme;
  hook_variant: HookVariant;
  endscreen: ScenePlanEndscreen;
  qa: ScenePlanQA;
}

/**
 * Props passed into the root <ScenePlanComposition>. The Brain CLI writes
 * the ScenePlan document to disk as-is (top-level fields, no wrapper key),
 * so `--props=scene_plan.json` must deep-merge directly onto these props —
 * wrapping it under a `scenePlan` key would mean the merge never touches
 * the real fields and the sample defaultProps gets rendered instead.
 */
export interface ScenePlanCompositionProps extends ScenePlan {
  // Index signature required to satisfy Remotion's `Record<string, unknown>`
  // constraint on composition props; does not change the contract shape.
  [key: string]: unknown;
}
