// sc08 · Light · U2 (873-952). ROOT: window closed from 873; counter 5 -> 9 on lightTicks (X3 x4); the LIGHT chip seats and
// the 'c' line lights red (cLit) ON lightSeat. U2 PICTURE: <LightBeamLive/> (engine: the beam races the rail from beamStart,
// X5 shimmer, reaches 'c' ON lightSeat, fades 924-950; mounted in sc09 too for its tail), <BeamIgnite/> (the beam's head at
// the foot ON beamStart itself, where the curve's progress is still 0 and the engine draws nothing) + <WallFlash/>: ON lightSeat the
// beam's white-cyan splash at its head and a pulse ON the red 'c' line (red only on the line), 12-14 f.
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { LightBeamLive } from "../../shared/Devices";
import { BeamIgnite, WallFlash } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Light: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <BeamIgnite />
      <LightBeamLive />
      <WallFlash />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
