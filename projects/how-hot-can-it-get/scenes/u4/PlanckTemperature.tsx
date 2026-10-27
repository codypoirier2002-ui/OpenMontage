// sc10 · PlanckTemperature · U4. "Beyond that waits the Planck temperature,"
// THE ROOT CARRIES THIS SCENE: the window closes (1141-1149), the camera drifts up to the Planck view (drift 1141-1181;
// every compact rung number shows), the Planck tick + 'Planck temperature' land ON planckMark (X3, 1181), the '?' dims to
// half, the zeros chip moves up under the Planck rung. U4 deliberately adds nothing here: the stage is the empty climb
// into darkness, and the hero number belongs to sc11 (it writes out from sciWrite). Seam 1141: U4 draws nothing before
// 1143 (BUILD §7) - this scene draws nothing at all. Hooks at the top (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import { useT } from "../../time";
import type { Mount, SceneProps } from "../../types";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const PlanckTemperature: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  void T;
  if (frame < from || frame >= to) return null;
  return null;
};
