// sc09 · Mercury. root: Mercury's orbit draws around the black hole from orbitDraw; the window closes from windowClose3. Here: a soft echo on the SGR A* rung as the orbit starts.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Mercury: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.orbitDraw} x={L.rail.x} y={T.railY(T.rung("sgra").L)} r0={6} r1={30} frames={14} strength={0.4} />
    </>
  );
};
