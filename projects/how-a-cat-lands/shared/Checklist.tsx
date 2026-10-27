// ROOT ONLY: THE PROCEDURE CHECKLIST CARD (the signature device, kept from video 14; props.checklist). A Ledger Paper card
// (L.card x 640-920, y 220-600), SEATED FROM FRAME 0 (lesson 34: the opening frame is never empty) and fixed to the end:
//   ELAPSED            (Roboto Mono 500 24 px)
//   0.00 s             (Roboto Mono 500 40 px; runs from 'First' at an ILLUSTRATIVE rate and STOPS on '06 LAND')
//   illustrative       (Roboto Mono 400 24 px: the clock's honesty tag, always beside it)
//   01 FIND UP ... 06 LAND  (Roboto Mono 500 24 px; a drawn tick box; the check mark DRAWS over TICK_F frames and is complete
//                      ON its tick frame = its X4 tick; a done row's text drops to 70 %)
// Constant after the last tick (the settle is still). Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { useT } from "../time";
import { CheckMark } from "./Icons";

export const CARD_ROW = { x: 20, y0: 150, pitch: 37, box: 24, textX: 56, size: 24 } as const;

export const ChecklistCard: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const CL = T.checklistInfo;
  const s = T.seat(frame, CL.seat, T.motion.SEAT_F, 9);
  if (!s.visible) return null;
  const b = L.card;
  const w = b.x1 - b.x0;
  const h = b.y1 - b.y0;
  const rows = T.check(frame);
  const clk = T.clock(frame);
  return (
    <div style={{ position: "absolute", left: b.x0 - s.y, top: b.y0, width: w, height: h, opacity: s.opacity }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: b.r, backgroundColor: C.paper, boxShadow: "0 16px 30px rgba(20,28,34,0.5), 0 2px 0 rgba(255,255,255,0.6) inset" }} />
      <div style={{ position: "absolute", left: w / 2 - 54, top: -2, width: 108, height: 20, borderRadius: 8, background: `linear-gradient(${C.steelLit}, ${C.steelEdge})`, boxShadow: "0 3px 6px rgba(20,28,34,0.4)" }} />
      <div style={{ position: "absolute", left: CARD_ROW.x, top: 26, fontFamily: FONT.mono, fontWeight: 500, fontSize: 24, letterSpacing: 2, color: C.paperInk }}>{CL.clockLabel}</div>
      <div style={{ position: "absolute", left: CARD_ROW.x, top: 54, fontFamily: FONT.mono, fontWeight: 500, fontSize: 40, letterSpacing: 1, color: C.paperInk, fontVariantNumeric: "tabular-nums" }}>{clk.text}</div>
      <div style={{ position: "absolute", left: CARD_ROW.x, top: 104, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.paperFaint }}>{CL.clockNote}</div>
      <div style={{ position: "absolute", left: 16, right: 16, top: 140, height: 2, backgroundColor: rgba(C.paperInk, 0.25) }} />
      <svg width={w} height={h} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        {rows.map((r, i) => {
          const y = CARD_ROW.y0 + i * CARD_ROW.pitch + 8;
          return (
            <g key={r.id}>
              <rect x={CARD_ROW.x} y={y} width={CARD_ROW.box} height={CARD_ROW.box} rx={4} fill={C.paper} stroke={C.paperInk} strokeWidth={2} />
              <CheckMark x={CARD_ROW.x - 1} y={y - 4} size={CARD_ROW.box + 6} progress={r.progress} />
            </g>
          );
        })}
      </svg>
      {rows.map((r, i) => (
        <div key={r.id} style={{ position: "absolute", left: CARD_ROW.textX, top: CARD_ROW.y0 + i * CARD_ROW.pitch + 8 + CARD_ROW.box / 2, transform: "translateY(-50%)",
          fontFamily: FONT.mono, fontWeight: 500, fontSize: CARD_ROW.size, color: C.paperInk, opacity: r.done ? 0.7 : 1, whiteSpace: "nowrap" }}>
          {r.text}
        </div>
      ))}
    </div>
  );
};
