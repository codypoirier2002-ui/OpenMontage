// sc01 · FloorLine · U1. The root draws the whole beat (the dark forge, the ember bed, the ice floor hairline on 'floor',
// '0 K = -273.15 °C' SEATED on T.sfx.floorLabelSeat with its X7 tick, 'the floor'). U1's optional cold accents were
// left out on review: the root's single ice line IS the callback, and anything more competes with it (art direction:
// 'the rest of the frame is unlit iron'). Nothing warm, nothing glowing. Hooks at the top (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import { useT } from "../../time";
import type { Mount, SceneProps } from "../../types";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const FloorLine: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  void T;
  return null;
};
