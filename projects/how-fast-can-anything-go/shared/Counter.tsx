// THE ZEROS COUNTER (ROOT ONLY: Composition.tsx mounts <Counter/> once; props.counter, build_props.py). A chip top right
// (theme.ts L.counter, right-aligned at x 920): 'ZEROS' in mono 22 px steel over one big slashed-zero digit (mono 500,
// 72 px, bone) = the order of magnitude of the marker's rung (digits after the first: 5 -> 0, 100 -> 2, 1,235 -> 3,
// 107,000 -> 5, 1,079,252,849 -> 9). The digit STEPS on its X3 tick frames (props.counter.ticks): a new digit drops in with
// a short gravity settle (T.seat, 4 f, 10 px) while the old one is cut on the tick frame itself, so the value shown ON the
// tick is the new one (lessons 4 / 22). Constant from the LIGHT seat (sc08) to the end. Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { useT } from "../time";

export const Counter: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const c = T.counter(frame);
  if (c.alpha <= 0) return null;
  const last = [...T.counterInfo.ticks].filter((f) => f <= frame).pop();
  const s = last === undefined ? { y: 0, k: 1 } : T.seat(frame, last + 4, 4, 10);
  const dy = last !== undefined && frame >= last ? s.y : 0;
  const b = L.counter;
  return (
    <div style={{ position: "absolute", left: b.x0, top: b.y0, width: b.x1 - b.x0, height: b.y1 - b.y0, display: "flex", justifyContent: "flex-end", opacity: c.alpha }}>
      <div style={{ height: "100%", padding: "0 22px 0 26px", display: "flex", alignItems: "center", gap: 18, borderRadius: 14, backgroundColor: rgba(C.chip, 0.9),
        border: `1.5px solid ${rgba(C.steel, 0.55)}` }}>
        <div style={{ fontFamily: FONT.mono, fontWeight: 400, fontSize: b.labelPx, letterSpacing: 2, color: C.steel, lineHeight: 1 }}>{T.counterInfo.label}</div>
        <div style={{ position: "relative", width: b.digitPx * 0.62, height: b.digitPx, overflow: "visible" }}>
          <div style={{ position: "absolute", left: 0, top: dy, fontFamily: FONT.mono, fontWeight: 500, fontSize: b.digitPx, lineHeight: 1, color: C.bone,
            fontVariantNumeric: "tabular-nums", textShadow: `0 0 18px ${rgba(C.bone, 0.25)}` }}>
            {c.value}
          </div>
        </div>
      </div>
    </div>
  );
};
