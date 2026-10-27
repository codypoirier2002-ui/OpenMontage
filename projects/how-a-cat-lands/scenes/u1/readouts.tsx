// U1 helper (sc02 + sc03): the two drawn readouts beside the S1 window, right column (x 640-920, y 620-780; the dials do
// not exist yet). Each chip FALLS and is fully seated ON its key frame (T.sfx.readouts[i]: 'nothing' 112, 'push' 131; no
// SFX), holds through the 1894 line, and is gone (opacity 0) by the 'IMPOSSIBLE?' stamp's first visible frame
// (stampImpossible - SEAT_F), because the stamp lands on the same column. Mounted by BOTH sc02 and sc03 with the same props,
// so the 161 / 162 seam is identical by construction. Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, E, FONT, L, rgba } from "../../theme";
import { prog, useT } from "../../time";
import { measure } from "../../shared/Type";

const PUSH_TEXT = "push: none";
const SPIN_TEXT = "starting spin: 0";
const SIZE = 28;
const ROWS = [
  { text: PUSH_TEXT, y: 664 },
  { text: SPIN_TEXT, y: 728 },
];
const X = L.card.x0; // 640: the chips' text starts here
const PAD = 10;

export const Readouts: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const stampFirst = T.sfx.stampImpossible - T.motion.SEAT_F; // the stamp's first visible frame
  const out = 1 - prog(frame, stampFirst - 14, stampFirst - 2, E.calm); // fully gone 2 f before the stamp shows
  if (out <= 0) return null;
  return (
    <>
      {ROWS.map((r, i) => {
        const s = T.seat(frame, T.sfx.readouts[i], T.motion.SEAT_F, 14);
        if (!s.visible) return null;
        const w = measure(r.text, "monoMed", SIZE);
        if (X + w > L.textRight) throw new Error(`readout '${r.text}' ends at x ${X + w} > ${L.textRight}`);
        return (
          <div key={i} style={{ position: "absolute", left: X - PAD, top: r.y + s.y, transform: "translateY(-50%)", height: SIZE + 18, width: w + 2 * PAD,
            boxSizing: "border-box", borderRadius: 8, backgroundColor: rgba(C.shadow, 0.84), border: `1.5px solid ${rgba(C.steelEdge, 0.9)}`,
            display: "flex", alignItems: "center", paddingLeft: PAD, opacity: s.opacity * out,
            fontFamily: FONT.mono, fontWeight: 500, fontSize: SIZE, color: C.bone, whiteSpace: "nowrap" }}>
            {r.text}
          </div>
        );
      })}
    </>
  );
};
