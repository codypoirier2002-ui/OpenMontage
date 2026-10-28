// sc08 · Proton. root: the window opens on windowOpen3 (the drawn detector tank), the marker waits on the red dwarf, "no decay seen" seats on noDecay. Here: nothing (the tank is the beat).
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Proton: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
