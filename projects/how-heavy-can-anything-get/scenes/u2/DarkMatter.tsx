// sc11 · DarkMatter. root: the DARK MATTER bar rises from darkRise and lands ON darkSeat with '~5 : 1 · inferred'. Here: nothing extra (the bar is the event).
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { useT } from "../../time";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const DarkMatter: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  void T;
  if (frame < from || frame >= to) return null;
  return null;
};
