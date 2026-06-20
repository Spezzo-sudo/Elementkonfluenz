import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import type {ScenePlanCompositionProps} from './sceneplan/types';
import {BarRace} from './components/BarRace';
import {EventOverlay} from './components/EventOverlay';
import {Endscreen} from './components/Endscreen';
import {IntroPhase} from './components/IntroPhase';

/**
 * Root composition. Reads ONLY the ScenePlan passed in via props — no
 * file IO, no Brain imports, no business logic. Selects which
 * phase-component to paint purely based on `duration.phases` frame ranges
 * that the Brain already computed.
 */
export const ScenePlanComposition: React.FC<ScenePlanCompositionProps> = (
  scenePlan,
) => {
  const frame = useCurrentFrame();
  const {phases} = scenePlan.duration;
  const {theme} = scenePlan;

  const inIntro = frame < phases.intro.end_frame;
  const inEndscreen = frame >= phases.endscreen.start_frame;
  // race + final_hold share the bar-race visualization; final_hold freezes
  // the camera/data sampling at the race's last frame (handled inside
  // BarRace itself), so no separate component is needed.
  const inRaceOrHold = !inIntro && !inEndscreen;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.colors.bg.primary ?? '#000000',
      }}
    >
      {inIntro && <IntroPhase scenePlan={scenePlan} />}

      {inRaceOrHold && (
        <>
          <BarRace scenePlan={scenePlan} />
          <EventOverlay scenePlan={scenePlan} />
        </>
      )}

      {inEndscreen && (
        <Endscreen
          scenePlan={scenePlan}
          phaseStartFrame={phases.endscreen.start_frame}
        />
      )}
    </AbsoluteFill>
  );
};
