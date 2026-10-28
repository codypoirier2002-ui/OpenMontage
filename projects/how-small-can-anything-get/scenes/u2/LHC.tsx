// sc11 · LHC · U2 (1203-1358). HERO 2. ROOT: the marker creeps to its final stop (14 px under 'c') ON creepEnd and the gap
// bracket + 'the gap' appear ON gapBracket ('hair', X6 tink). U2 PICTURE: <NinesReadoutLive/> (engine: the card 'LHC protons'
// seats ON readoutSeat with a gravity drop, no SFX; '99.9999991 %' lands one glyph per digitTick, X3 x10; constant after;
// mounted in sc12 too, same curves: seam 1358) + <StopPulse/>: ON gapBracket a small steel ring around the marker (under
// 'c') and a stop dash right of it, 16 f (over by 1315). Nothing else: the hero is the readout filling while the gap stays.
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { NinesReadoutLive } from "../../shared/Devices";
import { StopPulse } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const LHC: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StopPulse />
      <NinesReadoutLive />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
