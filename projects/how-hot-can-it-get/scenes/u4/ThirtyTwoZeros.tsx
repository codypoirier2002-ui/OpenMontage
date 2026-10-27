// sc11 · ThirtyTwoZeros ★ HERO 2 · U4. "roughly a one with thirty-two zeros, where our physics breaks."
// ROOT: the zeros chip counts 12 -> 32 on zeroTicks (X7 x20; '32 zeros' ON 'zeros' = sciWrite), the rail frays above the
// Planck mark on 'breaks' (fray, NO SFX) + 'where known physics stops working'.
// U4: '1.4 × 10^32 K' (shared <Sci>, the '32' drawn raised) WRITES OUT from sciWrite under the Planck label + zeros chip
// (./planck.tsx PlanckSci; the same element continues, constant, in sc12 and sc13). Hooks at the top (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { PlanckSci } from "./planck";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const ThirtyTwoZeros: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return <PlanckSci />;
};
