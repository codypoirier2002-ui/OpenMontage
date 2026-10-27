// sc08 · Light · U2. root: window closed; the LIGHT chip seats ON lightSeat, the 'c' line lights red (cLit), counter 5->9 (X3 x4). U2: <LightBeamLive/> (the beam races the rail beamStart -> lightSeat; X5 shimmer; fades after) - keep it mounted in sc09 too.
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { LightBeamLive } from "../../shared/Devices";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Light: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <LightBeamLive />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc08" from={from} to={to} />
    </>
  );
};
