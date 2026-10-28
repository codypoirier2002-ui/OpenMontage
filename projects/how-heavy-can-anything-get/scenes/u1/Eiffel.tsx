// sc03 · Eiffel. root: S2 (Eiffel Tower) crossfades in from plateSwap, the marker climbs from climbEiffel, EIFFEL TOWER seats on eiffelSeat, ZEROS 6..7; the window closes from windowClose1. Here: a ring on the seat.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Eiffel: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.eiffelSeat} x={L.rail.x} y={T.railY(T.rung("eiffel").L)} />
    </>
  );
};
