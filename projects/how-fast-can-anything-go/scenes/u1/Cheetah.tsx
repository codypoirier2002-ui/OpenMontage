// sc02 · Cheetah · U1. root: the window opens ON windowOpen1 (S1 placeholder until the still lands; 'AI impression'); the
// marker climbs from climbCheetah (X1) and the CHEETAH chip seats ON cheetahSeat; counter 0 -> 2 (X3 x2). U1: climb emphasis
// only (the plate is root): a bone flash on each decade tick the marker crosses (10, then 100 ON the seat) and one steel
// arrival ring from the marker ON cheetahSeat. Everything is gone 8 f before the FALCON page (lesson 42).
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { useT } from "../../time";
import { L } from "../../theme";
import { Ping, TickFlashes } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Cheetah: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  const r = T.rung("cheetah");
  return (
    <>
      <TickFlashes from={from} to={to} />
      <Ping at={r.seat} x={L.rail.x} y={T.railY(r.L)} />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
