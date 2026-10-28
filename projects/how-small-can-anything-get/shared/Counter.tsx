// THE ZEROS COUNTER (ROOT ONLY: Composition.tsx mounts <Counter/> once; props.counter, build_props.py). A chip top right
// (theme.ts L.counter, right-aligned at x 920): 'ZEROS' in mono 24 px steel beside the big slashed-zero number (mono 500,
// 72 px, bone) = the zeros after the decimal point of the active rung's metres (SAND 0.0005 m -> 3 ... PROTON -> 14), then the
// spin to 34 (the Planck length). Hidden before sandSeat. The number STEPS on its tick frames (props.counter.ticks): the new
// value is the one shown ON the tick, with a short gravity settle (lessons 4 / 22). Constant from spinEnd. Hooks at the top.

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
        <div style={{ position: "relative", width: b.digitPx * 0.6 * String(c.value).length, height: b.digitPx, overflow: "visible" }}>
          <div style={{ position: "absolute", left: 0, top: dy, fontFamily: FONT.mono, fontWeight: 500, fontSize: b.digitPx, lineHeight: 1, color: C.bone,
            fontVariantNumeric: "tabular-nums", textShadow: `0 0 18px ${rgba(C.bone, 0.25)}` }}>
            {c.value}
          </div>
        </div>
      </div>
    </div>
  );
};
