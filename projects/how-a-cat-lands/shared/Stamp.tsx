// THE STAMP (engine; from video 14's MissedStamp, re-inked Stamp red - stamps ONLY): 'IMPOSSIBLE?' (sc03) and 'NOT ALWAYS'
// (sc10). A double-rule rounded box, IBM Plex Sans Condensed 700, slightly rotated, a worn texture. `k` = T.seat(...).k: it
// drops / scales from 1.25 to 1 and is fully down ON the seat (the X3 thunk there; lessons 4, 22). The stamp sits OVER the
// window / the checklist card, so mount it in your scene's OVERLAY (the overlay plane is above both). Pass the text through
// a TEXT constant (literal scan). Pure (no hooks).

import React from "react";
import { C, FONT, rgba } from "../theme";

export const Stamp: React.FC<{ x: number; y: number; text: string; k: number; angle?: number; size?: number; opacity?: number }> = ({ x, y, text, k, angle = -8, size = 58, opacity = 1 }) => {
  if (k <= 0) return null;
  const sc = 1.25 - 0.25 * Math.min(1, k * k);
  const op = Math.min(1, k * 1.8) * 0.94 * opacity;
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%, -50%) rotate(${angle}deg) scale(${sc})`, opacity: op }}>
      <div style={{ padding: `${size * 0.14}px ${size * 0.42}px`, borderRadius: 14, border: `5px solid ${C.stamp}`, boxShadow: `inset 0 0 0 3px ${rgba(C.drapeDeep, 0.5)}, inset 0 0 0 6px ${C.stamp}`,
        backgroundColor: rgba(C.paper, 0.9), boxSizing: "border-box", fontFamily: FONT.display, fontWeight: 700, fontSize: size, lineHeight: 1.1,
        letterSpacing: size * 0.06, color: C.stamp, whiteSpace: "nowrap" }}>
        {text}
      </div>
    </div>
  );
};
