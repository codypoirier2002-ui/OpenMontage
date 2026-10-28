// sc07 · Neutron. root: the window opens on windowOpen2 (S3 neutron star); NEUTRON STAR seats beside SUN on neutronSeat (the marker does not move, ZEROS stays 30); the window closes from windowClose2. Here: a tight ring on the seat.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Neutron: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.neutronSeat} x={L.rail.x} y={T.railY(T.rung("neutron").L)} r0={4} r1={26} frames={14} />
    </>
  );
};
