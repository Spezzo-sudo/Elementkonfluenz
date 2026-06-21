import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {EmpireScenePlan} from '../../sceneplan/empireTypes';
import {empireGlow} from '../../sceneplan/empireTheme';

interface HookPhaseProps {
  scenePlan: EmpireScenePlan;
}

/**
 * Opening title card: two stacked hook_lines, fading + scaling in. Same
 * continuous interpolate() pattern as chart_race's IntroPhase — no
 * keyframe-snap, no business logic (line choice is the Brain's job).
 */
export const HookPhase: React.FC<HookPhaseProps> = ({scenePlan}) => {
  const frame = useCurrentFrame();
  const {theme, hook_lines, duration} = scenePlan;
  const phaseEnd = duration.phases.hook.end_frame;

  const fadeIn = Math.max(1, Math.min(14, Math.floor(phaseEnd / 4)));
  const opacity = interpolate(frame, [0, fadeIn], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const scale = interpolate(frame, [0, fadeIn], [0.82, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

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
        transform: `scale(${scale})`,
      }}
    >
      {hook_lines.map((line, i) => (
        <div
          key={i}
          style={{
            color: '#ffffff',
            fontSize: 84,
            fontWeight: 900,
            letterSpacing: 2,
            textAlign: 'center',
            textShadow: empireGlow(theme.accent_color),
          }}
        >
          {line}
        </div>
      ))}
    </div>
  );
};
