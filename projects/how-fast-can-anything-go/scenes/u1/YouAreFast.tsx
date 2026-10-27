// sc05 · YouAreFast · U1. HERO. root: the YOU tag seats at WALK on youSeat, JUMPS with the marker from jumpStart (X1 big) to EARTH on earthSeat (chip seats, counter 4->5 X3 x2). U1: <OrbitInset/> (drawn Sun / Earth / arrow + 'drawn · not to scale', alpha from orbitIn, gone before the PROBE page) + your emphasis on the jump.
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { OrbitInset } from "../../shared/Devices";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const YouAreFast: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <OrbitInset />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc05" from={from} to={to} />
    </>
  );
};
