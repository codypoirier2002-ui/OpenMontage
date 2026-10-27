// sc11 · LHC · U2. HERO 2. root: the marker creeps to its final stop ON creepEnd and the gap bracket 'the gap' appears (X6 tink). U2: <NinesReadoutLive/> (card seats ON readoutSeat; '99.9999991 %' lands one glyph per digitTick, X3 x10) - keep it mounted in sc12.
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { NinesReadoutLive } from "../../shared/Devices";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const LHC: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <NinesReadoutLive />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc11" from={from} to={to} />
    </>
  );
};
