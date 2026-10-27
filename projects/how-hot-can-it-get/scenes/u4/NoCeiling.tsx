// sc12 · NoCeiling · U4. "So heat may have no ceiling," - NO SFX from 'So' (asserted). Tab PROBABLY on 'So'.
// ROOT: the glow eases to its settle intensity (closingStart 1350-1395), the '?' fades out (qFade 1386-1406): the top
// stays open, dashed into darkness.
// U4: the hero number stays (constant, ./planck.tsx PlanckSci) and 'not a proven limit' (PROBABLY grammar: outline +
// hatch) is fully in ON 'ceiling' under it (ProvenNote). Hooks at the top (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { PlanckSci, ProvenNote } from "./planck";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const NoCeiling: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <PlanckSci />
      <ProvenNote />
    </>
  );
};
