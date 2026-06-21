import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {EmpireScenePlan} from '../../sceneplan/empireTypes';

interface ScalePhaseProps {
  scenePlan: EmpireScenePlan;
}

const SIDE_MARGIN = 64;
const BAR_HEIGHT = 64;
const BAR_GAP = 28;
const CHART_TOP = 320;

/**
 * Horizontal bar comparison (scale_comparison.rows[0] is always the owner,
 * `hero: true`, per the contract invariant — highlighted in accent_color,
 * the rest in a neutral tone). Bars grow from 0 via interpolate() driven by
 * the row's own index, so the hero doesn't have to finish first.
 */
export const ScalePhase: React.FC<ScalePhaseProps> = ({scenePlan}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const {theme, scale_comparison, duration} = scenePlan;
  const phase = duration.phases.scale;
  const phaseFrame = frame - phase.start_frame;

  // Bar track stops short of the full chart width, leaving a fixed-position
  // label column on the right — anchoring the value label there (instead of
  // right after the bar's own end) means the longest bar can never push its
  // label off-screen.
  const trackWidth = (width - 2 * SIDE_MARGIN) * 0.7;
  const maxValue = Math.max(...scale_comparison.rows.map((r) => r.value), 1);
  const growStagger = 8;

  return (
    <div style={{position: 'absolute', inset: 0}}>
      <div
        style={{
          position: 'absolute',
          top: 110,
          left: SIDE_MARGIN,
          right: SIDE_MARGIN,
          color: '#ffffff',
          fontSize: 40,
          fontWeight: 800,
          textAlign: 'center',
          lineHeight: 1.2,
        }}
      >
        {scale_comparison.headline}
      </div>

      {scale_comparison.rows.map((row, i) => {
        const top = CHART_TOP + i * (BAR_HEIGHT + BAR_GAP);
        const growStart = i * growStagger;
        const growEnd = growStart + 24;
        const grow = interpolate(phaseFrame, [growStart, growEnd], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const barWidth = (row.value / maxValue) * trackWidth * grow;
        const barColor = row.hero ? theme.accent_color : 'rgba(255,255,255,0.25)';

        return (
          <div key={row.label}>
            <div
              style={{
                position: 'absolute',
                left: SIDE_MARGIN,
                top: top - 30,
                color: row.hero ? theme.accent_color : 'rgba(255,255,255,0.85)',
                fontSize: 24,
                fontWeight: 700,
              }}
            >
              {row.label}
            </div>
            <div
              style={{
                position: 'absolute',
                left: SIDE_MARGIN,
                top,
                width: barWidth,
                height: BAR_HEIGHT,
                backgroundColor: barColor,
                borderRadius: 8,
              }}
            />
            <div
              style={{
                position: 'absolute',
                left: SIDE_MARGIN + trackWidth + 16,
                top,
                height: BAR_HEIGHT,
                display: 'flex',
                alignItems: 'center',
                color: '#ffffff',
                fontSize: 24,
                fontWeight: 700,
                whiteSpace: 'nowrap',
              }}
            >
              {row.value.toLocaleString('de-DE', {maximumFractionDigits: 1})}{' '}
              {scale_comparison.unit}
            </div>
          </div>
        );
      })}
    </div>
  );
};
