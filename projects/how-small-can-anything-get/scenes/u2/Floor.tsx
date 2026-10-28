// sc11 · Floor. root: the Planck line brightens ON floorGlow with 'a floor? unproven'. Here: a wide violet ring on the line.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { C, L } from "../../theme";


export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Floor: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.floorGlow} x={L.rail.x} y={T.dev.planck.y} color={C.planck} r1={90} />
    </>
  );
};
