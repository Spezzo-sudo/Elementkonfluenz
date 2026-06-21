import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {ScenePlan} from '../sceneplan/types';
import {glowBoxShadow, glowTextShadow} from '../sceneplan/theme';

interface IntroPhaseProps {
  scenePlan: ScenePlan;
}

interface VariantProps {
  scenePlan: ScenePlan;
  frame: number;
  fadeIn: number;
  opacity: number;
}

/**
 * Original/default layout: centered, scaling title card.
 */
const CenteredTitleIntro: React.FC<VariantProps> = ({scenePlan, frame, fadeIn, opacity}) => {
  const {theme, topic} = scenePlan;
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
          textShadow: glowTextShadow(theme.colors.accent.primary ?? '#ffffff', theme.glow_mode),
          textAlign: 'center',
        }}
      >
        {topic.assets.join(' vs ')}
      </div>
    </div>
  );
};

/**
 * First asset slides in from the left, last asset(s) from the right, with a
 * glowing "VS" divider between them.
 */
const SplitVsIntro: React.FC<VariantProps> = ({scenePlan, frame, fadeIn, opacity}) => {
  const {theme, topic} = scenePlan;
  const [first, ...rest] = topic.assets;
  const second = rest.join(' / ') || first;

  const slideProgress = interpolate(frame, [0, Math.max(1, fadeIn)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const offset = (1 - slideProgress) * 80;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 18,
        opacity,
        backgroundColor: theme.colors.bg.primary ?? '#000000',
        fontFamily: theme.font_family,
      }}
    >
      <div
        style={{
          transform: `translateX(${-offset}px)`,
          color: theme.colors.text.primary ?? '#ffffff',
          fontSize: 40,
          fontWeight: 800,
          textAlign: 'center',
        }}
      >
        {first}
      </div>
      <div
        style={{
          color: theme.colors.accent.primary ?? '#ffffff',
          fontSize: 26,
          fontWeight: 900,
          letterSpacing: 4,
          textShadow: glowTextShadow(theme.colors.accent.primary ?? '#ffffff', theme.glow_mode),
        }}
      >
        VS
      </div>
      <div
        style={{
          transform: `translateX(${offset}px)`,
          color: theme.colors.text.secondary ?? '#cccccc',
          fontSize: 40,
          fontWeight: 800,
          textAlign: 'center',
        }}
      >
        {second}
      </div>
    </div>
  );
};

/**
 * Each asset rotates/scales in as its own glowing "stamp" badge, staggered
 * by a few frames per badge for a cascade effect.
 */
const StampCascadeIntro: React.FC<VariantProps> = ({scenePlan, frame, fadeIn, opacity}) => {
  const {theme, topic} = scenePlan;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 14,
        padding: 40,
        opacity,
        backgroundColor: theme.colors.bg.primary ?? '#000000',
        fontFamily: theme.font_family,
      }}
    >
      {topic.assets.map((asset, i) => {
        const delay = i * 4;
        const localFrame = Math.max(0, frame - delay);
        const rotate = interpolate(localFrame, [0, Math.max(1, fadeIn)], [-18, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const localScale = interpolate(localFrame, [0, Math.max(1, fadeIn)], [0.5, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

        return (
          <div
            key={asset}
            style={{
              transform: `rotate(${rotate}deg) scale(${localScale})`,
              border: `3px solid ${theme.colors.accent.primary ?? '#ffffff'}`,
              borderRadius: 10,
              padding: '10px 18px',
              color: theme.colors.text.primary ?? '#ffffff',
              fontSize: 28,
              fontWeight: 800,
              boxShadow: glowBoxShadow(theme.colors.accent.primary ?? '#ffffff', theme.glow_mode),
            }}
          >
            {asset}
          </div>
        );
      })}
    </div>
  );
};

const INTRO_VARIANTS: Record<string, React.FC<VariantProps>> = {
  default: CenteredTitleIntro,
  split_vs: SplitVsIntro,
  stamp_cascade: StampCascadeIntro,
};

/**
 * Intro/hook title card. Layout is picked by `hook_variant.id` (unknown ids
 * fail open to the default layout rather than crashing the render); the
 * shared fade-in/out timing is computed once here so every variant stays in
 * sync with the intro phase boundaries.
 */
export const IntroPhase: React.FC<IntroPhaseProps> = ({scenePlan}) => {
  const frame = useCurrentFrame();
  const {duration, hook_variant} = scenePlan;
  const introEnd = duration.phases.intro.end_frame;

  const fadeIn = Math.max(1, Math.min(12, Math.floor(introEnd / 3)));
  const fadeOut = Math.max(1, Math.min(8, Math.floor(introEnd / 4)));
  const fadeOutStart = Math.max(fadeIn, introEnd - fadeOut);

  const opacity = interpolate(frame, [0, fadeIn, fadeOutStart, introEnd], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const Variant = INTRO_VARIANTS[hook_variant.id] ?? INTRO_VARIANTS.default;
  return <Variant scenePlan={scenePlan} frame={frame} fadeIn={fadeIn} opacity={opacity} />;
};
