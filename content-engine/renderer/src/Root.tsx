import React from 'react';
import {Composition, type CalculateMetadataFunction} from 'remotion';
import {ScenePlanComposition} from './Composition';
import {EmpireScenePlanComposition} from './EmpireComposition';
import type {ScenePlan, ScenePlanCompositionProps} from './sceneplan/types';
import type {
  EmpireScenePlan,
  EmpireScenePlanCompositionProps,
} from './sceneplan/empireTypes';
import sampleScenePlan from '../sample-scene-plan.json';
import sampleEmpireScenePlan from '../sample-empire-scene-plan.json';

/**
 * Derives composition metadata (fps, total frames, dimensions) from the
 * ScenePlan's own duration/fps fields, since different videos produced by
 * the Brain will have different lengths. This is the dynamic-duration
 * mechanism requested by the contract: width/height are fixed render
 * targets, but frames/fps come from the loaded ScenePlan.
 */
const calculateMetadata: CalculateMetadataFunction<
  ScenePlanCompositionProps
> = ({props}) => {
  return {
    durationInFrames: props.duration.total_frames,
    fps: props.fps,
    width: 1920,
    height: 1080,
  };
};

/**
 * Same dynamic-duration mechanism as ScenePlan's calculateMetadata, but for
 * the imperium vertical's EmpireScenePlan — and a portrait (1080x1920)
 * render target, since this vertical's source prototype (and the old
 * engine's render script) target Shorts/Reels framing, not the landscape
 * canvas chart_race uses.
 */
const calculateEmpireMetadata: CalculateMetadataFunction<
  EmpireScenePlanCompositionProps
> = ({props}) => {
  return {
    durationInFrames: props.duration.total_frames,
    fps: props.fps,
    width: 1080,
    height: 1920,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ScenePlan"
        component={ScenePlanComposition}
        durationInFrames={(sampleScenePlan as ScenePlan).duration.total_frames}
        fps={(sampleScenePlan as ScenePlan).fps}
        width={1920}
        height={1080}
        defaultProps={sampleScenePlan as ScenePlanCompositionProps}
        calculateMetadata={calculateMetadata}
      />
      <Composition
        id="EmpireScenePlan"
        component={EmpireScenePlanComposition}
        durationInFrames={
          (sampleEmpireScenePlan as EmpireScenePlan).duration.total_frames
        }
        fps={(sampleEmpireScenePlan as EmpireScenePlan).fps}
        width={1080}
        height={1920}
        defaultProps={sampleEmpireScenePlan as EmpireScenePlanCompositionProps}
        calculateMetadata={calculateEmpireMetadata}
      />
    </>
  );
};
