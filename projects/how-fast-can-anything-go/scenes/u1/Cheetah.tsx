// sc02 · Cheetah · U1. root: the window opens ON windowOpen1 (S1 placeholder until the still lands; 'AI impression'); the marker climbs from climbCheetah (X1) and the CHEETAH chip seats on cheetahSeat; counter 0->2 (X3 x2). U1: emphasis only (the plate is root).
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Cheetah: React.FC<SceneProps> = ({ from, to }) => {
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
      <StubLabel id="sc02" from={from} to={to} />
    </>
  );
};
