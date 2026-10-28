// sc10 · Universe. root: the rail BREAK draws from breakDraw, the UNIVERSE line + the ordinary bar appear on universeIn, ZEROS spins 36 -> 53 (53 ON spinEnd), the marker dims to a ghost. Here: a ring where the break leaves the rail.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Universe: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.breakDraw} x={L.rail.x} y={L.rail.breakY0} r0={6} r1={34} frames={16} strength={0.5} />
    </>
  );
};
