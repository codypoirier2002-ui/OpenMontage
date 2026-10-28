// sc01 · You. root: the rail draws bottom -> top from railDraw, YOU seats with its number on youSeat, ZEROS 1. Here: a glint riding the draw head + a ring on the YOU seat.
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

export const You: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <RailGlint />
      <Ping at={T.sfx.youSeat} x={L.rail.x} y={T.railY(T.rung("you").L)} />
    </>
  );
};
