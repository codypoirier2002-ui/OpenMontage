// sc10 · Energy · U2. root: the marker inches up (asymptotic creep). U2: <MassLabelLive/> + <EnergyLive/> ('ENERGY NEEDED' bar growing from barStart, OFF the top ON barOff (X3 accelerating ticks), the drawn gamma curve 'speed' / 'energy' + 'drawn · not to scale'; everything gone before the LHC page).
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { EnergyLive, MassLabelLive } from "../../shared/Devices";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Energy: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <MassLabelLive />
      <EnergyLive />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc10" from={from} to={to} />
    </>
  );
};
