// sc09 · Wall · U2. root: the marker leaves PARKER on wallStart and climbs toward 'c', slowing (no SFX). U2: <LightBeamLive/> (its fade-out tail) + <MassLabelLive/> ('anything with mass', fixed chip + leader to the marker; gone before the LHC page).
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { LightBeamLive, MassLabelLive } from "../../shared/Devices";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Wall: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <LightBeamLive />
      <MassLabelLive />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc09" from={from} to={to} />
    </>
  );
};
