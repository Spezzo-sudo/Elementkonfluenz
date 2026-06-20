import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {ScenePlan} from '../sceneplan/types';
import {glowTextShadow} from '../sceneplan/theme';

interface EndscreenProps {
  scenePlan: ScenePlan;
  phaseStartFrame: number;
}

/**
 * Final summary screen showing endscreen.final_values. Fades in smoothly
 * relative to the start of the endscreen phase via `interpolate()`.
 */
export const Endscreen: React.FC<EndscreenProps> = ({
  scenePlan,
  phaseStartFrame,
}) => {
  const frame = useCurrentFrame();
  const {endscreen, theme} = scenePlan;

  const opacity = interpolate(
    frame,
    [phaseStartFrame, phaseStartFrame + 15],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        opacity,
        backgroundColor: theme.colors.bg.primary ?? '#000000',
        fontFamily: theme.font_family,
      }}
    >
      <div
        style={{
          color: theme.colors.text.primary ?? '#ffffff',
          fontSize: 40,
          fontWeight: 800,
          marginBottom: 32,
          textShadow: glowTextShadow(
            theme.colors.accent.primary ?? '#ffffff',
            theme.glow_mode,
          ),
        }}
      >
        Final Results
      </div>
      {endscreen.final_values.map((fv) => {
        const isPositive = fv.gain_pct >= 0;
        const gainColor = isPositive
          ? theme.colors.accent.positive ?? '#22c55e'
          : theme.colors.accent.negative ?? '#ef4444';

        return (
          <div
            key={fv.ticker}
            style={{
              display: 'flex',
              gap: 24,
              alignItems: 'baseline',
              fontSize: 28,
              marginBottom: 12,
              color: theme.colors.text.primary ?? '#ffffff',
            }}
          >
            <span style={{fontWeight: 700, minWidth: 140}}>{fv.ticker}</span>
            <span>
              {fv.value.toLocaleString(undefined, {maximumFractionDigits: 2})}
            </span>
            <span style={{color: gainColor, fontWeight: 700}}>
              {isPositive ? '+' : ''}
              {fv.gain_pct.toFixed(1)}%
            </span>
          </div>
        );
      })}
    </div>
  );
};
