// sc02 · CeilingQuestion · U1. The root draws the whole beat (the 40 px camera tilt on T.sfx.camTilt, the filament '?'
// drawing from T.sfx.qStart with its X3 peak, the dashed spine from T.sfx.spineStart). U1 adds nothing: the '?' is the
// only warm element allowed before the sweep, and the question beat reads cleanest as rail + '?' alone. Hooks at the top.
import React from "react";
import { useCurrentFrame } from "remotion";
import { useT } from "../../time";
import type { Mount, SceneProps } from "../../types";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const CeilingQuestion: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  void T;
  return null;
};
