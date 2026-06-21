import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {EmpireScenePlan} from '../../sceneplan/empireTypes';
import {empireGlow} from '../../sceneplan/empireTheme';

interface FactsPhaseProps {
  scenePlan: EmpireScenePlan;
}

const CROSSFADE_FRAMES = 10;

/**
 * Cycles through facts (already capped to 3 by the Brain's builder.py),
 * one big number per slot, with a short crossfade at each boundary so the
 * transition isn't a hard cut. Slot length is derived from the phase's own
 * duration, not hardcoded, so a future Brain change to fact count/phase
 * length keeps working without a renderer edit.
 */
export const FactsPhase: React.FC<FactsPhaseProps> = ({scenePlan}) => {
  const frame = useCurrentFrame();
  const {theme, facts, duration} = scenePlan;
  const phase = duration.phases.facts;
  const phaseFrame = frame - phase.start_frame;
  const phaseLen = Math.max(1, phase.end_frame - phase.start_frame);
  const slotLen = phaseLen / Math.max(facts.length, 1);

  return (
    <div style={{position: 'absolute', inset: 0}}>
      {facts.map((fact, i) => {
        const slotStart = i * slotLen;
        const slotEnd = slotStart + slotLen;
        const fade = Math.min(CROSSFADE_FRAMES, slotLen / 2);
        const opacity = interpolate(
          phaseFrame,
          [slotStart, slotStart + fade, slotEnd - fade, slotEnd],
          [0, 1, 1, 0],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        if (opacity <= 0.001) {
          return null;
        }

        return (
          <div
            key={fact.label}
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
                fontSize: 30,
                fontWeight: 800,
                letterSpacing: 4,
                marginBottom: 12,
              }}
            >
              {fact.label}
            </div>
            <div
              style={{
                color: '#ffffff',
                fontSize: 130,
                fontWeight: 900,
                lineHeight: 1,
                textShadow: empireGlow(theme.accent_color),
              }}
            >
              {fact.display_value}
            </div>
            <div
              style={{
                color: 'rgba(255,255,255,0.8)',
                fontSize: 34,
                fontWeight: 700,
                marginTop: 8,
              }}
            >
              {fact.unit}
            </div>
            <div
              style={{
                color: 'rgba(255,255,255,0.6)',
                fontSize: 22,
                fontWeight: 500,
                marginTop: 28,
                textAlign: 'center',
                maxWidth: 800,
              }}
            >
              {fact.description} ({fact.year})
            </div>
          </div>
        );
      })}
    </div>
  );
};
