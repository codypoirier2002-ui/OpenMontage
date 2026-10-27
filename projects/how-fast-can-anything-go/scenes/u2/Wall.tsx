// sc09 · Wall · U2 (952-1025). ROOT: the marker leaves PARKER ON wallStart ('nothing') and climbs toward 'c', slowing (the
// asymptotic creep; no SFX). U2 PICTURE: <LightBeamLive/> (its tail: alpha 0 from 950, so nothing shows; kept for the seam),
// <CreepTrail/> (a stroboscopic steel trail on the spine behind the marker: the tick spacing shrinks as it slows; alpha =
// T.mass, so it comes with 'anything with mass' and is gone 1197, before the LHC page) and <MassLabelLive/> (engine: the
// fixed chip 'anything with mass' + its dotted leader to the marker, from massLabel). Both trail and label continue in sc10
// from the same curves (seam 1025).
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { LightBeamLive, MassLabelLive } from "../../shared/Devices";
import { CreepTrail } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Wall: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <LightBeamLive />
      <CreepTrail />
      <MassLabelLive />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
