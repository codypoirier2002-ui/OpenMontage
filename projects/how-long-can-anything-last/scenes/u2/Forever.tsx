// sc12 · Forever. root: the dashed forever? line draws up through the break from foreverDraw (no sound: the closing sentence is SFX-free), the finished line, the release, the CTA on ctaFrame; every channel constant from the release (lesson 25). Here: nothing.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Forever: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
