// sc01 · Sand. root: the rail draws top -> bottom from railDraw (X1), SAND seats with its number on sandSeat, ZEROS 3, the window opens on windowOpen1 (S1). Here: a glint riding the draw head + a ring on the SAND seat.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";
import { RailGlint } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Sand: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <RailGlint />
      <Ping at={T.sfx.sandSeat} x={L.rail.x} y={T.railY(T.rung("sand").L)} />
    </>
  );
};
