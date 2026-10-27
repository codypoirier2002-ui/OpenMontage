// sc04 · Sound · U1. root: window closed; climb from climbSound (X1), SOUND chip ON soundSeat (X2 thump); counter 3. U1:
// <PressureRing from={T.sfx.soundSeat}/> (the device: one soft ring from the marker ON the seat, 24 f) + the sound-wave
// hint: two faint steel bow arcs ahead of the marker while it climbs (the air it pushes), gone ON the seat where the ring
// takes over; a decade-tick flash as it crosses 1,000. Everything is gone 8 f before the ORBIT page (lesson 42).
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { PressureRing } from "../../shared/Devices";
import { useT } from "../../time";
import { BowWave, TickFlashes } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Sound: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <TickFlashes from={from} to={to} />
      <BowWave from={T.sfx.climbSound} seat={T.sfx.soundSeat} />
      <PressureRing from={T.sfx.soundSeat} />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
