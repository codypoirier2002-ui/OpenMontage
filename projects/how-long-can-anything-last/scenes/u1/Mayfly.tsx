// sc01 · Mayfly. root: the rail draws bottom -> top from railDraw, MAYFLY seats with its number on mayflySeat, ZEROS 0. Here: a glint riding the draw head + a ring on the MAYFLY seat.
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

export const Mayfly: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <RailGlint />
      <Ping at={T.sfx.mayflySeat} x={L.rail.x} y={T.railY(T.rung("mayfly").L)} />
    </>
  );
};
