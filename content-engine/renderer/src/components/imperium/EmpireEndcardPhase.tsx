import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {EmpireScenePlan} from '../../sceneplan/empireTypes';

interface EmpireEndcardPhaseProps {
  scenePlan: EmpireScenePlan;
}

/**
 * Closing stock-performance card — the vertical's one live-fetched data
 * point (see builder.py's _download_stock_endcard). "$1.000 -> $1.528"
 * formatting follows the design notes' explicit finding (section 7:
 * unicode arrow, no "Dollar"/"->" text) over the old prototype's wording.
 */
export const EmpireEndcardPhase: React.FC<EmpireEndcardPhaseProps> = ({
  scenePlan,
}) => {
  const frame = useCurrentFrame();
  const {theme, endcard, duration} = scenePlan;
  const phase = duration.phases.endcard;
  const phaseFrame = frame - phase.start_frame;

  const opacity = interpolate(phaseFrame, [0, 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const isPositive = endcard.gain_pct >= 0;
  const gainColor = isPositive ? '#22c55e' : '#ef4444';

  const fmt = (value: number) =>
    `$${value.toLocaleString('de-DE', {maximumFractionDigits: 0})}`;

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
      }}
    >
      <div
        style={{
          color: theme.accent_color,
          fontSize: 26,
          fontWeight: 800,
          letterSpacing: 3,
          marginBottom: 28,
        }}
      >
        {endcard.ticker_label}
      </div>
      <div
        style={{
          color: '#ffffff',
          fontSize: 76,
          fontWeight: 900,
          whiteSpace: 'nowrap',
        }}
      >
        {fmt(endcard.stock_from)} → {fmt(endcard.stock_to)}
      </div>
      <div
        style={{
          color: gainColor,
          fontSize: 48,
          fontWeight: 800,
          marginTop: 24,
        }}
      >
        {isPositive ? '+' : ''}
        {endcard.gain_pct.toLocaleString('de-DE', {maximumFractionDigits: 1})}%
      </div>
      <div
        style={{
          position: 'absolute',
          bottom: 90,
          left: 64,
          right: 64,
          textAlign: 'center',
          color: 'rgba(255,255,255,0.55)',
          fontSize: 18,
          fontStyle: 'italic',
        }}
      >
        {endcard.disclaimer}
      </div>
    </div>
  );
};
