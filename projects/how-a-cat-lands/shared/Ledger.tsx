// THE LEDGER (engine; NEW for video 15; units mount it in sc11-sc12): a Ledger Paper card (L.ledger x 140-920, y 630-1010)
// with the title across the top, the study's rows on the left and, on the right (from x L.ledger.ghostX0, below the title), the HATCHED, EMPTY ghost column of the cats
// that never reached a vet. Every string is passed in (route them through TEXT / LABEL constants in your scene so
// build_props.py's literal scan checks them against verified_on_screen_strings):
//   title   '1987 · Animal Medical Center, NY'      rows   ['132 cats · high-rise falls']
//   bar     0..1 fill of the survival bar (to ~90 % of its width at 1); barLabel '~90% survived' (the '~' drawn tall)
//   ghost   0..1 the ghost column drawing in (header 'never reached a vet', cell 'not counted' at `notCounted` 0..1)
//   bracket 0..1 the bracket under the bar + 'of cats brought in' (so ~90 % is never on screen without its caveat once the
//           closing sentence starts: lesson 16)
//   k       0..1 the card's seat (pass T.seat(...).k; it drops with a gravity ease and is fully down ON T.sfx.ledgerSeat, X7)
// The bar is a drawing of the study's number: it reads ~90 % of the bar's length (measured value, MEASURED tab); the ghost
// column carries NO number (nothing was counted: PROBABLY). Pure (no hooks).

import React from "react";
import { C, FONT, L, rgba } from "../theme";
import { Rich, hatch } from "./Type";

export const Ledger: React.FC<{
  k: number; dropY?: number; title: string; rows: string[]; bar: number; barLabel: string;
  ghost: number; ghostHeader: string; notCounted: number; notCountedText: string; bracket: number; bracketText: string; opacity?: number;
}> = ({ k, dropY = 0, title, rows, bar, barLabel, ghost, ghostHeader, notCounted, notCountedText, bracket, bracketText, opacity = 1 }) => {
  if (k <= 0) return null;
  const B = L.ledger;
  const w = B.x1 - B.x0;
  const h = B.y1 - B.y0;
  const gx = B.ghostX0 - B.x0;
  const barX = 28, barY = 196, barW = gx - 64, barH = 44;
  const mono: React.CSSProperties = { fontFamily: FONT.mono, fontWeight: 500, color: C.paperInk, whiteSpace: "nowrap", position: "absolute" };
  return (
    <div style={{ position: "absolute", left: B.x0, top: B.y0 + dropY, width: w, height: h, opacity: Math.min(1, k * 1.6) * opacity }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 14, backgroundColor: C.paper, boxShadow: "0 16px 30px rgba(28,43,42,0.45)" }} />
      {/* ruled lines */}
      {[90, 160, 290].map((y) => <div key={y} style={{ position: "absolute", left: 18, right: 18, top: y, height: 2, backgroundColor: rgba(C.paperInk, 0.18) }} />)}
      <div style={{ ...mono, left: 28, top: 32, fontSize: 27 }}>{title}</div>
      {rows.map((r, i) => <div key={i} style={{ ...mono, left: 28, top: 112 + i * 40, fontSize: 28, fontWeight: 400 }}>{r}</div>)}
      {/* the survival bar (a measured value: ~90 % of its length) */}
      <div style={{ position: "absolute", left: barX, top: barY, width: barW, height: barH, borderRadius: 6, border: `2.5px solid ${C.paperInk}`, boxSizing: "border-box" }} />
      <div style={{ position: "absolute", left: barX + 4, top: barY + 4, width: (barW - 8) * 0.9 * Math.max(0, Math.min(1, bar)), height: barH - 8, borderRadius: 3,
        backgroundColor: C.drapeDeep }} />
      {bar >= 1 ? (
        <div style={{ ...mono, left: barX, top: barY + barH + 10, fontSize: 30, fontFamily: FONT.display, fontWeight: 700 }}>
          <Rich text={barLabel} size={30} color={C.paperInk} />
        </div>
      ) : null}
      {bracket > 0 ? (
        <svg width={w} height={h} style={{ position: "absolute", inset: 0, opacity: bracket }}>
          <path d={`M ${barX + 2} ${barY + barH + 66} L ${barX + 2} ${barY + barH + 78} L ${barX + (barW - 8) * 0.9} ${barY + barH + 78} L ${barX + (barW - 8) * 0.9} ${barY + barH + 66}`}
            stroke={C.paperInk} strokeWidth={3} fill="none" />
        </svg>
      ) : null}
      {bracket > 0 ? <div style={{ ...mono, left: barX, top: barY + barH + 88, fontSize: 26, fontWeight: 400, opacity: bracket }}>{bracketText}</div> : null}
      {/* the ghost column: hatched, EMPTY, dashed outline - draws in from the top */}
      {ghost > 0 ? (
        <div style={{ position: "absolute", left: gx, top: 108, width: w - gx - 18, height: (h - 126) * Math.min(1, ghost), overflow: "hidden", borderRadius: 10,
          border: `2.5px dashed ${C.paperFaint}`, backgroundImage: hatch(C.paperFaint, 0.35, 9), boxSizing: "border-box" }}>
          <div style={{ ...mono, left: 14, top: 14, width: w - gx - 64, whiteSpace: "normal", lineHeight: 1.2, fontSize: 24, color: C.paperInk, fontWeight: 500, backgroundColor: C.paper, padding: "2px 6px", borderRadius: 4 }}>{ghostHeader}</div>
          {notCounted > 0 ? (
            <div style={{ ...mono, left: 14, top: 128, fontSize: 26, color: C.paperInk, opacity: notCounted, backgroundColor: C.paper, padding: "2px 6px", borderRadius: 4 }}>{notCountedText}</div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
};
