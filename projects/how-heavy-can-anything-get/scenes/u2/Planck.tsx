// sc09 · Planck. root: the rail BREAK draws from breakDraw, the violet PLANCK line is in ON planckIn, the counter spins 14 -> 34 (spinStart -> spinEnd). Here: a violet ring where the line meets the rail.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { C, L } from "../../theme";


export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Planck: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.planckIn} x={L.rail.x} y={T.dev.planck.y} color={C.planck} r1={44} />
    </>
  );
};
