import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import type {EmpireScenePlanCompositionProps} from './sceneplan/empireTypes';
import {HookPhase} from './components/imperium/HookPhase';
import {RegisterCardsPhase} from './components/imperium/RegisterCardsPhase';
import {BeatPhase} from './components/imperium/BeatPhase';
import {StampPhase} from './components/imperium/StampPhase';
import {FactsPhase} from './components/imperium/FactsPhase';
import {ScalePhase} from './components/imperium/ScalePhase';
import {EmpireEndcardPhase} from './components/imperium/EmpireEndcardPhase';

/**
 * Root composition for the imperium vertical. Reads ONLY EmpireScenePlan
 * props — no file IO, no Brain imports, no business logic. Picks exactly
 * one phase component per frame based on `duration.phases`, which the Brain
 * already computed (see content-engine/EMPIRE_SCENE_PLAN.md).
 */
export const EmpireScenePlanComposition: React.FC<
  EmpireScenePlanCompositionProps
> = (scenePlan) => {
  const frame = useCurrentFrame();
  const {phases} = scenePlan.duration;

  let body: React.ReactNode = null;
  if (frame < phases.hook.end_frame) {
    body = <HookPhase scenePlan={scenePlan} />;
  } else if (frame < phases.register_cards.end_frame) {
    body = <RegisterCardsPhase scenePlan={scenePlan} />;
  } else if (frame < phases.beat.end_frame) {
    body = <BeatPhase scenePlan={scenePlan} />;
  } else if (frame < phases.stamp.end_frame) {
    body = <StampPhase scenePlan={scenePlan} />;
  } else if (frame < phases.facts.end_frame) {
    body = <FactsPhase scenePlan={scenePlan} />;
  } else if (frame < phases.scale.end_frame) {
    body = <ScalePhase scenePlan={scenePlan} />;
  } else {
    body = <EmpireEndcardPhase scenePlan={scenePlan} />;
  }

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#111113',
        fontFamily:
          "'Helvetica Neue', 'Segoe UI', Arial, sans-serif",
      }}
    >
      {body}
    </AbsoluteFill>
  );
};
