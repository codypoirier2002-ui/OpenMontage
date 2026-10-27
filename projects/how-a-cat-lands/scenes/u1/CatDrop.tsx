// sc01 · CatDrop (U1). 'Drop a cat upside down, and it flips over in midair'
// ROOT: the rig, the header, the checklist card, 'drawn · not to scale' from frame 0; the clamp is FULLY OPEN ON clampOpen
// (X1 click). U1: <CatLive/> - the curves hang the cat upside down under the clamp, drop it (gravity) and flip it feet-down
// as a quick preview (front tucks, turns; legs swap; back turns) by previewFlipEnd, then turn it into a ghost outline (the
// later scenes explain the flip). No explanation here: the only addition is a few faint STEEL fall streaks above the cat,
// whose length and opacity follow the curve's own fall speed (T.cat(f).y - T.cat(f - 1).y), so they start on the first
// moving frame after the release and are gone once the cat stops. Steel only (amber / cyan are the halves' own).
// Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { CatLive, CAT } from "../../shared/Cat";
import { C, L, rgba } from "../../theme";
import { useT } from "../../time";
import { noise1 } from "../../shared/noise";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

// streak columns relative to the waist (x offsets across the body) and their phase
const STREAKS = [
  { dx: -150, ph: 0.0 },
  { dx: -70, ph: 0.37 },
  { dx: 15, ph: 0.71 },
  { dx: 95, ph: 0.19 },
  { dx: 170, ph: 0.55 },
];

export const CatDrop: React.FC<SceneProps> = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const pose = T.cat(frame);
  const prev = T.cat(Math.max(0, frame - 1));
  const vy = Math.max(0, pose.y - prev.y); // px / frame (the curve's gravity fall)
  const k = Math.min(1, vy / 5); // full at ~5 px / frame
  const top = pose.y - CAT.halfH - CAT.legOut - 18; // above the highest leg / paw
  return (
    <>
      {k > 0.02 ? (
        <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
          {STREAKS.map((s, i) => {
            const len = 30 + 70 * k * (0.7 + 0.3 * noise1(`fall${i}`, frame * 0.21 + s.ph));
            const y0 = Math.max(L.rig.jawY + 8, top - 6 - 22 * s.ph);
            const y1 = Math.max(L.rig.jawY + 8, y0 - len);
            if (y0 - y1 < 6) return null;
            return (
              <line key={i} x1={pose.x + s.dx} y1={y0} x2={pose.x + s.dx} y2={y1} stroke={rgba(C.steelLit, 0.42 * k)} strokeWidth={4} strokeLinecap="round" />
            );
          })}
        </svg>
      ) : null}
      <CatLive />
    </>
  );
};
