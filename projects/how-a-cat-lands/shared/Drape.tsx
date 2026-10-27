// ROOT ONLY: the slate drape of the test lab (the ground, frame 0 to the end): Drape #3B4A55 with a static woven texture
// (code, ~3 % luma: two crossed fine line patterns), the lab light (a soft lit pool top-centre, deeper slate at the edges)
// and two soft folds. Fully STATIC (no drift): the settle is still by construction. useId() unconditional (lesson 1). From video 14.

import React, { useId } from "react";
import { AbsoluteFill } from "remotion";
import { AMBIENT, C, rgba } from "../theme";
import { cssId } from "./noise";

export const Drape: React.FC = () => {
  const id = cssId(useId(), "drape");
  const a = AMBIENT.weave;
  return (
    <AbsoluteFill style={{ backgroundColor: C.drape }}>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <radialGradient id={`${id}-light`} cx="0.5" cy="0.28" r="0.75">
            <stop offset="0" stopColor={C.drapeLit} stopOpacity={0.95} />
            <stop offset="0.55" stopColor={C.drape} stopOpacity={0} />
            <stop offset="1" stopColor={C.drapeDeep} stopOpacity={0.9} />
          </radialGradient>
          <pattern id={`${id}-weave`} width={6} height={6} patternUnits="userSpaceOnUse">
            <path d="M 0 0 L 6 0" stroke={rgba("#FFFFFF", a * 2.2)} strokeWidth={1} />
            <path d="M 0 3 L 6 3" stroke={rgba("#000000", a * 1.6)} strokeWidth={1} />
            <path d="M 1.5 0 L 1.5 6" stroke={rgba("#000000", a * 1.2)} strokeWidth={1} />
            <path d="M 4.5 0 L 4.5 6" stroke={rgba("#FFFFFF", a * 1.4)} strokeWidth={1} />
          </pattern>
        </defs>
        <rect width={1080} height={1920} fill={`url(#${id}-light)`} />
        <rect width={1080} height={1920} fill={`url(#${id}-weave)`} />
        {/* two soft drape folds (static) */}
        <path d="M -40 1180 C 260 1140, 640 1230, 1120 1150" stroke={rgba(C.drapeDeep, 0.35)} strokeWidth={60} fill="none" />
        <path d="M -40 240 C 300 280, 700 200, 1120 260" stroke={rgba(C.drapeDeep, 0.22)} strokeWidth={46} fill="none" />
      </svg>
    </AbsoluteFill>
  );
};
