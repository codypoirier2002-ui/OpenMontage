// sc08 · SgrA. root: the window opens on windowOpen3 (the DRAWN black hole), the marker climbs from climbSgra, ZEROS 31..36 on sgraTicks, SGR A* seats on sgraSeat. Here: a ring on the seat.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const SgrA: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.sgraSeat} x={L.rail.x} y={T.railY(T.rung("sgra").L)} r1={56} frames={20} />
    </>
  );
};
