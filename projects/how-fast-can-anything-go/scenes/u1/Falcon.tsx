// sc03 · Falcon · U1. root: S1 -> S2 crossfade from plateSwap (hard tag swap at the midpoint); climb from climbFalcon (X1), FALCON chip + hatched 'commonly cited' on falconSeat (PROBABLY tab); window closes windowClose1. U1: emphasis only.
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Falcon: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc03" from={from} to={to} />
    </>
  );
};
