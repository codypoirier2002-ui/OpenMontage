// sc09 · Limit. root: the long climb from climbProton, ZEROS 12 -> 33 accelerating (33 ON protonSeat), the PROTON rung seats as a lower limit, the rail BREAK draws from breakDraw. Here: a wide ring on the seat.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Limit: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.protonSeat} x={L.rail.x} y={T.railY(T.rung("proton").L)} r1={64} frames={22} />
    </>
  );
};
