/**
 * Pure interpolation helpers. These contain NO decision logic — they only
 * continuously interpolate between control points/keyframes that the Brain
 * already computed. This is the concrete fix for the old matplotlib
 * stutter: instead of snapping to the nearest keyframe per redraw, every
 * value here is a continuous function of `frame` produced by Remotion's
 * `interpolate()`.
 */
import {interpolate, Easing} from 'remotion';
import type {CameraKeyframe, TimeMapControlPoint} from './types';

export interface CameraBounds {
  x_min: number;
  x_max: number;
  y_min: number;
  y_max: number;
}

/**
 * Interpolates camera bounds for an arbitrary (possibly fractional) frame
 * value by running four independent `interpolate()` calls — one per bound
 * — across the full keyframe array. Remotion's `interpolate` performs
 * piecewise-linear interpolation between *all* provided input points, so a
 * frame that lies between keyframe[i] and keyframe[i+1] yields a smoothly
 * blended value, not the nearest keyframe's value.
 */
export function interpolateCameraBounds(
  frame: number,
  keyframes: CameraKeyframe[],
): CameraBounds {
  if (keyframes.length === 0) {
    return {x_min: 0, x_max: 1, y_min: 0, y_max: 1};
  }
  if (keyframes.length === 1) {
    const only = keyframes[0];
    return {
      x_min: only.x_min,
      x_max: only.x_max,
      y_min: only.y_min,
      y_max: only.y_max,
    };
  }

  const sorted = [...keyframes].sort((a, b) => a.frame - b.frame);
  const frames = sorted.map((k) => k.frame);

  const interpOpts = {
    easing: Easing.inOut(Easing.ease),
    extrapolateLeft: 'clamp' as const,
    extrapolateRight: 'clamp' as const,
  };

  return {
    x_min: interpolate(frame, frames, sorted.map((k) => k.x_min), interpOpts),
    x_max: interpolate(frame, frames, sorted.map((k) => k.x_max), interpOpts),
    y_min: interpolate(frame, frames, sorted.map((k) => k.y_min), interpOpts),
    y_max: interpolate(frame, frames, sorted.map((k) => k.y_max), interpOpts),
  };
}

/**
 * Maps a render frame to a (fractional) data-series index using the
 * time_map control points, via linear interpolation between them. A
 * fractional result (e.g. 4.3) is intentional: callers should lerp between
 * data_index floor/ceil samples for sub-frame-accurate motion instead of
 * snapping to an integer index.
 */
export function frameToDataIndex(
  frame: number,
  controlPoints: TimeMapControlPoint[] | undefined,
  fallbackMaxIndex: number,
): number {
  if (!controlPoints || controlPoints.length === 0) {
    // No time remapping: assume render frame == data index 1:1, clamped.
    return Math.min(Math.max(frame, 0), fallbackMaxIndex);
  }
  if (controlPoints.length === 1) {
    return controlPoints[0].data_index;
  }

  const sorted = [...controlPoints].sort((a, b) => a.frame - b.frame);
  return interpolate(
    frame,
    sorted.map((p) => p.frame),
    sorted.map((p) => p.data_index),
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    },
  );
}

/**
 * Samples a numeric series at a fractional index by linearly interpolating
 * between the two nearest integer samples. Non-numeric entries are treated
 * as "hold previous value" so malformed input can't crash the render.
 */
export function sampleSeriesAtIndex(
  values: Array<number | string>,
  fractionalIndex: number,
): number {
  const numeric = values.map((v) => (typeof v === 'number' ? v : NaN));
  const lastValid = (() => {
    let prev = 0;
    return numeric.map((v) => {
      if (!Number.isNaN(v)) {
        prev = v;
        return v;
      }
      return prev;
    });
  })();

  const clampedIndex = Math.min(
    Math.max(fractionalIndex, 0),
    lastValid.length - 1,
  );
  const lowerIndex = Math.floor(clampedIndex);
  const upperIndex = Math.min(lowerIndex + 1, lastValid.length - 1);
  const t = clampedIndex - lowerIndex;

  const lowerValue = lastValid[lowerIndex] ?? 0;
  const upperValue = lastValid[upperIndex] ?? lowerValue;

  return interpolate(t, [0, 1], [lowerValue, upperValue], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
}

/**
 * Continuous fade in / hold / fade out opacity for an event overlay window,
 * computed as a function of `frame` via `interpolate()`. This avoids any
 * "is frame inside window" boolean snap — opacity ramps smoothly across a
 * configurable number of frames at each edge.
 */
export function eventOpacity(
  frame: number,
  frameStart: number,
  frameEnd: number,
  fadeFrames: number = 10,
): number {
  const safeFade = Math.max(
    1,
    Math.min(fadeFrames, Math.floor((frameEnd - frameStart) / 2) || 1),
  );

  return interpolate(
    frame,
    [
      frameStart - safeFade,
      frameStart,
      frameEnd,
      frameEnd + safeFade,
    ],
    [0, 1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    },
  );
}
