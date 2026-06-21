import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {EmpireScenePlan} from '../../sceneplan/empireTypes';

interface StampPhaseProps {
  scenePlan: EmpireScenePlan;
}

/**
 * Registry-stamp reveal: owner identity card slams in, then a rotated
 * "ink stamp" impacts on top. The impact uses `spring()` (Remotion's
 * physically-damped easing) instead of a linear interpolate — this is the
 * one moment in the vertical the design notes explicitly call out as
 * needing a "punch" (see IMPERIUM_DESIGN_EXPERIMENT_V1_3: 10-frame impact,
 * scale 1.35 -> 1).
 */
export const StampPhase: React.FC<StampPhaseProps> = ({scenePlan}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {theme, owner, duration} = scenePlan;
  const phase = duration.phases.stamp;
  const phaseFrame = frame - phase.start_frame;

  const cardOpacity = interpolate(phaseFrame, [0, 6], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const stampImpactFrame = 6;
  const stampProgress = spring({
    frame: phaseFrame - stampImpactFrame,
    fps,
    config: {damping: 12, stiffness: 220, mass: 0.6},
  });
  const stampScale = interpolate(stampProgress, [0, 1], [1.35, 1]);
  const stampOpacity = interpolate(
    phaseFrame,
    [stampImpactFrame, stampImpactFrame + 4],
    [0, 0.92],
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
        opacity: cardOpacity,
      }}
    >
      <div
        style={{
          position: 'relative',
          width: 860,
          padding: '48px 56px',
          backgroundColor: 'rgba(20,20,20,0.92)',
          border: `2px solid ${theme.accent_color}`,
          borderRadius: 12,
          boxShadow: '0 12px 36px rgba(0,0,0,0.5)',
        }}
      >
        <div
          style={{
            color: '#ffffff',
            fontSize: 80,
            fontWeight: 900,
            lineHeight: 1.05,
          }}
        >
          {owner.display_name}
        </div>
        <div
          style={{
            color: 'rgba(255,255,255,0.75)',
            fontSize: 26,
            fontWeight: 600,
            marginTop: 18,
          }}
        >
          {owner.legal_name}
        </div>
        <div
          style={{
            color: 'rgba(255,255,255,0.6)',
            fontSize: 22,
            fontWeight: 500,
            marginTop: 6,
          }}
        >
          {owner.hq_city} · gegründet {owner.founded_year}
        </div>

        <div
          style={{
            position: 'absolute',
            right: 36,
            top: '50%',
            transform: `translateY(-50%) rotate(-9deg) scale(${stampScale})`,
            opacity: stampOpacity,
            border: `5px solid ${theme.stamp_color}`,
            borderRadius: 8,
            padding: '10px 22px',
            color: theme.stamp_color,
            fontSize: 28,
            fontWeight: 900,
            letterSpacing: 2,
            whiteSpace: 'nowrap',
          }}
        >
          REGISTRIERT
        </div>
      </div>
    </div>
  );
};
