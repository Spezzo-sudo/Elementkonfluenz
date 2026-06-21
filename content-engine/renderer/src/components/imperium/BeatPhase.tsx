import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {EmpireScenePlan} from '../../sceneplan/empireTypes';
import {empireGlow} from '../../sceneplan/empireTheme';

interface BeatPhaseProps {
  scenePlan: EmpireScenePlan;
}

/**
 * Short connective beat line between the card cascade and the stamp reveal
 * (e.g. "ALLE SPUREN FUEHREN ZU EINEM NAMEN"). Deliberately brief — the
 * Brain already sized this phase short (1.5s) in _PHASE_SECONDS.
 */
export const BeatPhase: React.FC<BeatPhaseProps> = ({scenePlan}) => {
  const frame = useCurrentFrame();
  const {theme, beat_line, duration} = scenePlan;
  const phase = duration.phases.beat;
  const phaseFrame = frame - phase.start_frame;
  const phaseLen = Math.max(1, phase.end_frame - phase.start_frame);

  const fadeEdge = Math.max(1, Math.min(10, Math.floor(phaseLen / 3)));
  const opacity = interpolate(
    phaseFrame,
    [0, fadeEdge, phaseLen - fadeEdge, phaseLen],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0 90px',
        opacity,
      }}
    >
      <div
        style={{
          color: '#ffffff',
          fontSize: 46,
          fontWeight: 800,
          textAlign: 'center',
          letterSpacing: 1,
          textShadow: empireGlow(theme.accent_color),
        }}
      >
        {beat_line}
      </div>
    </div>
  );
};
