// sc13 · EdgeOfKnowing · U4. "just an edge to what we know." - NO SFX; release knowEndFrame 1461, chord 1466, CTA 1465.
// ROOT: the whole ladder floor -> Planck in the low blue-white glow (i 0.42), every root channel constant from 1461.
// U4: the calm finale adds NOTHING new: the hero number and 'not a proven limit' simply stay, fully settled since ~1386,
// so nothing of U4 moves after 1386 and the settle (1461-1506) is still (lesson 25). Hooks at the top (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { PlanckSci, ProvenNote } from "./planck";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const EdgeOfKnowing: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <PlanckSci />
      <ProvenNote />
    </>
  );
};
