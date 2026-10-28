// sc05 · Virus. root: S2 -> S3 from plateSwap2, VIRUS seats on virusSeat (ZEROS 6), 'LIGHT MICROSCOPE' draws ON lightLine, the window closes from windowClose1. Here: rings on the seat and the line.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";


export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Virus: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.virusSeat} x={L.rail.x} y={T.railY(T.rung("virus").L)} />
      <Ping at={T.sfx.lightLine} x={L.rail.x} y={T.railY(T.dev.refs[1].L)} r1={34} />
    </>
  );
};
