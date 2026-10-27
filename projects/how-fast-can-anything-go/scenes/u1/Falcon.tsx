// sc03 · Falcon · U1. root: S1 -> S2 crossfade from plateSwap (hard tag swap at the midpoint); climb from climbFalcon (X1),
// FALCON chip + hatched 'commonly cited' ON falconSeat (PROBABLY tab); window closes windowClose1. U1: climb emphasis only:
// decade-tick flashes (none are crossed on this climb: 100 -> ~390) and one steel arrival ring ON falconSeat (no SFX there:
// the counter stays at 2). Gone 8 f before the SOUND page (lesson 42).
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { useT } from "../../time";
import { L } from "../../theme";
import { Ping, TickFlashes } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Falcon: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  const r = T.rung("falcon");
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
