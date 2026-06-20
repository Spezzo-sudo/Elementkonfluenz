import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {ScenePlan} from '../sceneplan/types';
import {glowTextShadow} from '../sceneplan/theme';

interface IntroPhaseProps {
  scenePlan: ScenePlan;
}

/**
 * Simple intro/hook title card driven by hook_variant.id and topic.assets.
 * Fades + scales in via `interpolate()` (no spring needed for a one-shot
 * title card, but kept continuous either way).
 */
export const IntroPhase: React.FC<IntroPhaseProps> = ({scenePlan}) => {
  const frame = useCurrentFrame();
  const {theme, topic, duration} = scenePlan;
  const introEnd = duration.phases.intro.end_frame;

  // Fade-in/out edge widths shrink for very short intro phases so the
  // input range to interpolate() always stays strictly increasing.
  const fadeIn = Math.max(1, Math.min(12, Math.floor(introEnd / 3)));
  const fadeOut = Math.max(1, Math.min(8, Math.floor(introEnd / 4)));
  const fadeOutStart = Math.max(fadeIn, introEnd - fadeOut);

  const opacity = interpolate(
    frame,
    [0, fadeIn, fadeOutStart, introEnd],
    [0, 1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    },
  );
  const scale = interpolate(frame, [0, Math.max(1, fadeIn)], [0.85, 1], {
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
        backgroundColor: theme.colors.bg.primary ?? '#000000',
        fontFamily: theme.font_family,
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          color: theme.colors.text.primary ?? '#ffffff',
          fontSize: 44,
          fontWeight: 800,
          textShadow: glowTextShadow(
            theme.colors.accent.primary ?? '#ffffff',
            theme.glow_mode,
          ),
          textAlign: 'center',
        }}
      >
        {topic.assets.join(' vs ')}
      </div>
    </div>
  );
};
