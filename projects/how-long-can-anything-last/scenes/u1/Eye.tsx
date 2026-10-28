// sc03 · Eye. root: the dashed 'YOUR EYE' line draws ON eyeLine and the veil dims the rail below it. Here: a ring where the line crosses the rail.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { L } from "../../theme";


export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Eye: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.eyeLine} x={L.rail.x} y={T.railY(T.dev.refs[0].L)} />
    </>
  );
};
