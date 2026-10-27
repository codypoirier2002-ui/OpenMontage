import React from "react";
import { Composition } from "remotion";
import { SpeedLadder, calculateMetadata } from "./Composition";
import { DEFAULT_PROPS } from "./props.generated";

// 1080x1920 @ 30 fps; duration = props.timeline.total_frames (calculateMetadata).
// defaultProps = props.generated.ts (identical to artifacts/props.json, both from build_props.py).
export const Root: React.FC = () => (
  <Composition
    id="SpeedLadder"
    component={SpeedLadder}
    durationInFrames={DEFAULT_PROPS.timeline.total_frames}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={DEFAULT_PROPS}
    calculateMetadata={calculateMetadata}
  />
);
