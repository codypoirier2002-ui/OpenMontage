// sc10 · Energy · U2 (1025-1203). ROOT: the marker inches up (the creep slows further). U2 PICTURE: <CreepTrail/> (continued
// from sc09, same curves), <MassLabelLive/> (continued; out 1185-1197), <EnergyLive/> (engine: 'ENERGY NEEDED' in ON
// energyIn, the bar grows from barStart on the X3 bar ticks, accelerating, OFF the top ON barOff 'end'; the drawn gamma curve
// 'speed' / 'energy' with 'drawn · not to scale'; out 1185-1197 = energyOut) + <StepMarks/>: 'each step' - a steel mark
// right of the bar at its height ON each bar tick; the gaps between the marks grow (each step costs more); alpha = the
// energy alpha, so everything of this claim is gone 1197, 8 f before the LHC page (1205; glide from 1199).
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { EnergyLive, MassLabelLive } from "../../shared/Devices";
import { CreepTrail, StepMarks } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Energy: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <CreepTrail />
      <MassLabelLive />
      <EnergyLive />
      <StepMarks />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
