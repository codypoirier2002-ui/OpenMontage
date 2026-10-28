// L5 film grain (copied from projects/how-a-cat-lands/shared/Grain.tsx, video 15; itself videos 12-14): ONCE, at the root
// (2 %, refreshed on twos), above every scene, below the overlay plane.
// Grain seed = T.driftFrame(T.loopFrame(frame)) on twos (lesson 11, loopFrame FIRST): from props.settle.freezeFrom (the
// release of 'way.') loopFrame returns 0, so the grain freezes on frame 0's seed and the settle is still.
// useId() is called unconditionally at the top of the component (lesson 1).

import React, { useId } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { AMBIENT } from "../theme";
import { useT } from "../time";
import { cssId } from "./noise";

export const Grain: React.FC<{ amount?: number }> = ({ amount = AMBIENT.grain }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const id = cssId(useId(), "g");
  const seedFrame = T.driftFrame(T.loopFrame(frame));
  const seed = (seedFrame - (seedFrame % 2)) % 997; // on twos
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="1080" height="1920" style={{ position: "absolute", inset: 0, opacity: amount * 4, mixBlendMode: "overlay" }}>
        <filter id={id}>
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={seed} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="1080" height="1920" filter={`url(#${id})`} />
      </svg>
    </AbsoluteFill>
  );
};
