import React from 'react';
import {Composition, type CalculateMetadataFunction} from 'remotion';
import {ScenePlanComposition} from './Composition';
import type {ScenePlan, ScenePlanCompositionProps} from './sceneplan/types';
import sampleScenePlan from '../sample-scene-plan.json';

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
  const {scenePlan} = props;
  return {
    durationInFrames: scenePlan.duration.total_frames,
    fps: scenePlan.fps,
    width: 1920,
    height: 1080,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="ScenePlan"
      component={ScenePlanComposition}
      durationInFrames={(sampleScenePlan as ScenePlan).duration.total_frames}
      fps={(sampleScenePlan as ScenePlan).fps}
      width={1920}
      height={1080}
      defaultProps={{
        scenePlan: sampleScenePlan as ScenePlan,
      }}
      calculateMetadata={calculateMetadata}
    />
  );
};
