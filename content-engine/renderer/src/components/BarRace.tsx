import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import type {ScenePlan} from '../sceneplan/types';
import {
  frameToDataIndex,
  interpolateCameraBounds,
  sampleSeriesAtIndex,
} from '../sceneplan/interpolation';
import {glowBoxShadow, glowTextShadow} from '../sceneplan/theme';

interface BarRaceProps {
  scenePlan: ScenePlan;
}

/**
 * Bar-race visualization for the `race` phase (and reused, frozen at the
 * final frame, during `final_hold`).
 *
 * Camera bounds and the frame->data-index mapping are both continuous
 * functions of `frame` (see sceneplan/interpolation.ts), so bar
 * position/width/scale change smoothly every single frame instead of
 * jumping between the Brain's sparse keyframes/control-points. This is the
 * direct replacement for the old matplotlib `fig.canvas.draw()` full-redraw
 * stutter.
 */
export const BarRace: React.FC<BarRaceProps> = ({scenePlan}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  const {camera, data_series, theme, duration} = scenePlan;

  // Freeze camera/data sampling at the end of the race phase during
  // final_hold, so the bars don't keep animating once we're meant to hold.
  const raceEnd = duration.phases.race.end_frame;
  const effectiveFrame = Math.min(frame, raceEnd);

  const bounds = interpolateCameraBounds(effectiveFrame, camera.keyframes);

  const maxDataLen = Math.max(
    1,
    ...data_series.map((s) => s.values.length - 1),
  );

  const fractionalIndex = frameToDataIndex(
    effectiveFrame,
    scenePlan.time_map?.enabled ? scenePlan.time_map.control_points : undefined,
    maxDataLen,
  );

  const chartLeft = 0.12 * width;
  const chartRight = 0.95 * width;
  const chartTop = 0.18 * height;
  const chartBottom = 0.88 * height;
  const chartWidth = chartRight - chartLeft;
  const chartHeight = chartBottom - chartTop;

  const yRange = Math.max(bounds.y_max - bounds.y_min, 1e-6);

  const barHeight = Math.min(64, chartHeight / Math.max(data_series.length, 1) - 16);

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        fontFamily: theme.font_family,
      }}
    >
      {data_series.map((series, i) => {
        const value = sampleSeriesAtIndex(series.values, fractionalIndex);
        const clampedValue = Math.min(Math.max(value, bounds.y_min), bounds.y_max);
        const normalized = (clampedValue - bounds.y_min) / yRange;
        const barWidth = Math.max(0, normalized * chartWidth);

        const top = chartTop + i * (barHeight + 16);

        return (
          <div key={series.ticker}>
            <div
              style={{
                position: 'absolute',
                left: chartLeft,
                top,
                width: barWidth,
                height: barHeight,
                backgroundColor: series.color,
                borderRadius: 6,
                boxShadow: glowBoxShadow(series.color, theme.glow_mode),
                transition: 'none',
              }}
            />
            <div
              style={{
                position: 'absolute',
                left: chartLeft + 12,
                top: top + barHeight / 2,
                transform: 'translateY(-50%)',
                color: theme.colors.text.primary ?? '#ffffff',
                fontWeight: 700,
                fontSize: Math.max(14, barHeight * 0.32),
                textShadow: glowTextShadow(series.color, theme.glow_mode),
                whiteSpace: 'nowrap',
              }}
            >
              {series.label}
            </div>
            <div
              style={{
                position: 'absolute',
                left: chartLeft + barWidth + 16,
                top: top + barHeight / 2,
                transform: 'translateY(-50%)',
                color: theme.colors.text.secondary ?? theme.colors.text.primary ?? '#ffffff',
                fontWeight: 600,
                fontSize: Math.max(13, barHeight * 0.28),
                whiteSpace: 'nowrap',
              }}
            >
              {clampedValue.toLocaleString(undefined, {
                maximumFractionDigits: 2,
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};
