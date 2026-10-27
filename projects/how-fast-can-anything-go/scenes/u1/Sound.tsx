// sc04 · Sound · U1. root: window closed; climb from climbSound (X1), SOUND chip ON soundSeat (X2 thump); counter 3. U1: <PressureRing from={T.sfx.soundSeat}/> (the demo) - one soft ring from the marker.
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { PressureRing } from "../../shared/Devices";
import { useT } from "../../time";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Sound: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <PressureRing from={T.sfx.soundSeat} />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc04" from={from} to={to} />
    </>
  );
};
