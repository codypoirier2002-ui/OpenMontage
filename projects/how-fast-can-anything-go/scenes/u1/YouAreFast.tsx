// sc05 · YouAreFast · U1. HERO. root: the YOU tag seats at WALK ON youSeat, JUMPS with the marker from jumpStart (X1 big)
// to EARTH ON earthSeat (chip seats, counter 4 -> 5 X3 x2). U1: <OrbitInset/> (the device: drawn Sun / Earth / arrow +
// 'drawn · not to scale', alpha from orbitIn, gone before the PROBE page) + the jump's emphasis: <JumpTrail/> (a dashed
// ghost where the tag sat at WALK, a dashed trail with a chevron following the tag up the rail, a launch ring ON jumpStart,
// the tag's box flashing once ON earthSeat; all gone 24 f after the seat) and decade-tick flashes as the marker crosses
// 10,000 and 100,000. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { OrbitInset } from "../../shared/Devices";
import { JumpTrail, TickFlashes } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const YouAreFast: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <TickFlashes from={from} to={to} />
      <JumpTrail />
      <OrbitInset />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
