// sc02 · Whale. root: the window opens on windowOpen1 (S1 whale), the marker climbs from climbWhale, BLUE WHALE seats on whaleSeat, ZEROS 2..5 on whaleTicks. Here: a ring on the seat.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Whale: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.whaleSeat} x={L.rail.x} y={T.railY(T.rung("whale").L)} />
    </>
  );
};
