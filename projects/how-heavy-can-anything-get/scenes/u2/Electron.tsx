// sc08 · Electron. root: the bracket + open arrow + 'ELECTRON' from electronIn, 'no size found' seats on noSize; the marker does not move. Here: a ring at the bracket on noSize.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";


export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Electron: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.noSize} x={L.rail.x} y={L.rail.y1} />
    </>
  );
};
