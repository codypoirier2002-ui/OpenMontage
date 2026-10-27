// THE LADDER RAIL (ROOT ONLY: Composition.tsx mounts <Ladder/> once; it reads props.ladder through useT() and draws, on
// every frame). Pattern of projects/how-hot-can-it-get/shared/Ladder.tsx (video 13) without the black-body colour / camera:
//   the RAIL       a steel log10(km/h) spine at x 250 from y 1080 (1 km/h) up to the 'c' line at y 380; dim from frame 0
//                  (lesson 34: something to look at), DRAWS bright foot -> top on 'You' (railDraw, X1); decade ticks
//                  x 236-264 with their numbers ('1' ... '100,000,000', mono 18 px, right-aligned at x 224; the 10^9 tick
//                  carries no number: 'c' sits 2.6 px above it); 'km/h · log scale' under the foot.
//   the 'c' LINE   RED (the only red on screen), y 380, x 222-278, + the red 'c' right of... left of the rail; dim (0.3)
//                  until the light beam reaches it (cLit -> 1 ON lightSeat, sc08).
//   the RUNGS      a tick per rung dropping onto y = railY(L) ON its seat frame (T.seat) WITH its label chip (name in Saira
//                  700 28 px + number in IBM Plex Mono 500 28 px, slashed zeros; two-line chips for EARTH and PARKER so no
//                  chip ever sits under the open window: build_props asserts), i.e. only when the marker arrives (lessons
//                  33 / 46). The FALCON chip carries the hatched PROBABLY chip 'commonly cited'. Chips are de-overlapped
//                  bottom-up with thin leaders (SOUND sits 39 px above FALCON).
//   the MARKER     the white-cyan bead (r 6 + glow) at railY(markerL) with speed STREAKS behind it while it moves
//                  (length = log10(speed)-scaled), breathing on the loop clock; it never touches 'c' (build_props asserts).
//   the GAP        a tiny bracket on the rail's left between 'c' and the marker + 'the gap' (sc11 ->, X6).
// Everything is a pure function of the frame (no state). Hooks at the top (lesson 1). No blend modes (lesson 24).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { prog, useT } from "../time";
import type { Timing } from "../time";
import type { Rung } from "../types";
import { Rich, hatch, measure } from "./Type";

const R = L.rail;
const LABEL_PX = 28;
const CHIP_PAD = 12;
const ROW_H = 36;
const CHIP_GAP = 6;
const DECADES = ["1", "10", "100", "1,000", "10,000", "100,000", "1,000,000", "10,000,000", "100,000,000", "1,000,000,000"];

type Placed = { rung: Rung; want: number; y: number; h: number; w: number; drop: number; alpha: number };

const chipHeight = (r: Rung) => r.lines.length * ROW_H + (r.chip ? 32 : 0) + 8;
const chipWidth = (r: Rung) => {
  let w = 0;
  for (const line of r.lines) {
    if (line.includes(" · ")) {
      const [name, num] = line.split(" · ");
      w = Math.max(w, measure(name, "display", LABEL_PX) + measure(" · ", "display", LABEL_PX) + measure(num, "monoMed", LABEL_PX));
    } else w = Math.max(w, /^[~\d,]+$/.test(line) ? measure(line, "monoMed", LABEL_PX) : measure(line, "display", LABEL_PX));
  }
  if (r.chip) w = Math.max(w, measure(r.chip, "mono", 24) + 20);
  return w + 2 * CHIP_PAD;
};

/** de-overlap bottom-up: each chip sits at its wanted y or above the one below it; never above cY - 24 (the LIGHT chip is the top one) */
const deoverlap = (items: Placed[]) => {
  const s = [...items].sort((a, b) => b.want - a.want);
  let prevTop = Infinity;
  for (const it of s) {
    it.y = Math.min(it.want, prevTop - it.h / 2 - CHIP_GAP);
    prevTop = it.y - it.h / 2;
  }
  return s;
};

const Line: React.FC<{ line: string }> = ({ line }) => {
  if (line.includes(" · ")) {
    const [name, num] = line.split(" · ");
    return (
      <span style={{ whiteSpace: "nowrap" }}>
        <span style={{ fontFamily: FONT.display, fontWeight: 700 }}>{name}</span>
        <span style={{ fontFamily: FONT.display, fontWeight: 700, color: C.steel }}> · </span>
        <span style={{ fontFamily: FONT.mono, fontWeight: 500, fontVariantNumeric: "tabular-nums" }}><Rich text={num} size={LABEL_PX} /></span>
      </span>
    );
  }
  const isNum = /^[~\d,]+$/.test(line);
  return (
    <span style={{ fontFamily: isNum ? FONT.mono : FONT.display, fontWeight: isNum ? 500 : 700, whiteSpace: "nowrap", fontVariantNumeric: "tabular-nums" }}>
      <Rich text={line} size={LABEL_PX} />
    </span>
  );
};

const Rungs: React.FC<{ T: Timing; frame: number }> = ({ T, frame }) => {
  const placed: Placed[] = [];
  const ticks: React.ReactNode[] = [];
  for (const g of T.rungs) {
    const s = T.seat(frame, g.seat, T.motion.SEAT_F, 18);
    if (!s.visible) continue;
    const y = T.railY(g.L) + s.y;
    ticks.push(
      <div key={g.id} style={{ position: "absolute", left: R.rungX0, top: y - 2.5, width: R.rungX1 - R.rungX0, height: 5, borderRadius: 3, opacity: s.opacity,
        backgroundColor: C.steel, boxShadow: s.seated ? `0 0 10px ${rgba(C.steel, 0.5)}` : "none" }} />,
    );
    placed.push({ rung: g, want: T.railY(g.L), y: 0, h: chipHeight(g), w: chipWidth(g), drop: s.y, alpha: s.opacity });
  }
  const laid = deoverlap(placed);
  return (
    <>
      {ticks}
      {laid.map((p) => {
        const lead = Math.abs(p.y - p.want) > 3;
        const top = p.y - p.h / 2 + p.drop;
        return (
          <React.Fragment key={p.rung.id}>
            {lead ? (
              <svg width={R.labelX - R.rungX1 + 2} height={Math.abs(p.y - p.want) + 6} style={{ position: "absolute", left: R.rungX1 - 1, top: Math.min(p.y, p.want) - 3, overflow: "visible", opacity: p.alpha }}>
                <path d={`M 0 ${p.want > p.y ? Math.abs(p.y - p.want) + 3 : 3} L ${R.labelX - R.rungX1} ${p.want > p.y ? 3 : Math.abs(p.y - p.want) + 3}`} stroke={rgba(C.steel, 0.6)} strokeWidth={1.5} fill="none" />
              </svg>
            ) : null}
            <div style={{ position: "absolute", left: R.labelX, top, width: p.w, height: p.h, boxSizing: "border-box", padding: `4px ${CHIP_PAD}px`, borderRadius: 10,
              backgroundColor: rgba(C.chip, 0.88), border: `1px solid ${rgba(C.steel, 0.35)}`, opacity: p.alpha, color: C.bone, fontSize: LABEL_PX, lineHeight: `${ROW_H}px` }}>
              {p.rung.lines.map((line, i) => (
                <div key={i} style={{ height: ROW_H }}><Line line={line} /></div>
              ))}
              {p.rung.chip ? (
                <div style={{ marginTop: 2, display: "inline-block", height: 28, lineHeight: "26px", padding: "0 10px", borderRadius: 14, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24,
                  color: C.bone, border: `1.5px solid ${rgba(C.bone, 0.9)}`, backgroundImage: hatch(C.bone, 0.16), boxSizing: "border-box", whiteSpace: "nowrap" }}>
                  {p.rung.chip}
                </div>
              ) : null}
            </div>
          </React.Fragment>
        );
      })}
    </>
  );
};

const Spine: React.FC<{ T: Timing; frame: number }> = ({ T, frame }) => {
  const ld = T.ladder(frame);
  const you = T.you(frame);
  const gapTop = T.cY;
  const drawn = R.axisY0 - (R.axisY0 - R.cY) * ld.railDraw;
  return (
    <>
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
        {/* the dim rail from frame 0, the bright one drawing over it foot -> 'c' */}
        <line x1={R.x} y1={R.axisY0} x2={R.x} y2={R.cY} stroke={C.steelDim} strokeWidth={3} opacity={0.55} />
        {ld.railDraw > 0 ? <line x1={R.x} y1={R.axisY0} x2={R.x} y2={drawn} stroke={C.steel} strokeWidth={3} opacity={0.9} /> : null}
        {DECADES.map((_, d) => {
          const y = T.railY(d);
          const a = 0.35 + 0.45 * prog(y, drawn, drawn + 1) * 0 + 0.45 * (ld.railDraw >= 1 || y >= drawn ? 1 : 0);
          return <line key={d} x1={R.tickX0} y1={y} x2={R.tickX1} y2={y} stroke={C.steelDim} strokeWidth={2} opacity={a} />;
        })}
        {/* THE 'c' LINE: the only red on screen */}
        <line x1={R.tickX0 - 14} y1={R.cY} x2={R.tickX1 + 14} y2={R.cY} stroke={C.wall} strokeWidth={3} opacity={0.35 + 0.65 * ld.cLit} />
        {ld.cLit > 0.5 ? <line x1={R.tickX0 - 14} y1={R.cY} x2={R.tickX1 + 14} y2={R.cY} stroke={C.wall} strokeWidth={9} opacity={0.22 * ld.cLit} /> : null}
        {/* the gap bracket (left of the rail, between 'c' and the marker's final position) */}
        {ld.gap > 0 ? (
          <g opacity={ld.gap} stroke={C.steel} strokeWidth={2} fill="none" strokeLinecap="round">
            <path d={`M ${L.gap.x + 6} ${gapTop + 2} L ${L.gap.x} ${gapTop + 2} L ${L.gap.x} ${ld.y - 1} L ${L.gap.x + 6} ${ld.y - 1}`} />
            <path d={`M ${L.gap.x} ${(gapTop + ld.y) / 2} L ${L.gap.x - 8} ${(gapTop + ld.y) / 2}`} />
          </g>
        ) : null}
      </svg>
      {DECADES.slice(0, 9).map((txt, d) => {
        const y = T.railY(d);
        const nearYou = you.alpha > 0 && Math.abs(y - you.y) < 26;
        const a = (y >= drawn || ld.railDraw >= 1 ? 0.8 : 0.4) * (nearYou ? 0 : 1);
        return (
          <div key={d} style={{ position: "absolute", right: L.W - R.numRight, top: y - 11, fontFamily: FONT.mono, fontWeight: 400, fontSize: 18, lineHeight: "22px", color: C.steelDim,
            opacity: a, whiteSpace: "nowrap", fontVariantNumeric: "tabular-nums" }}>
            {txt}
          </div>
        );
      })}
      {/* 'c' (red) left of the rail at the line */}
      <div style={{ position: "absolute", right: L.W - R.numRight, top: R.cY - 19, fontFamily: FONT.display, fontWeight: 700, fontSize: 30, lineHeight: "38px", color: C.wall,
        opacity: 0.4 + 0.6 * ld.cLit, textShadow: ld.cLit > 0.5 ? `0 0 14px ${rgba(C.wall, 0.6 * ld.cLit)}` : "none" }}>
        {T.labels.c}
      </div>
      {ld.gap > 0 ? (
        <div style={{ position: "absolute", right: L.W - L.gap.labelRight, top: gapTop + 26, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "28px",
          color: C.steel, opacity: ld.gap, whiteSpace: "nowrap" }}>
          {T.labels.gap}
        </div>
      ) : null}
      <div style={{ position: "absolute", left: L.axisLabel.x, top: L.axisLabel.y - 14, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "28px", color: C.steel,
        opacity: 0.55 + 0.35 * ld.railDraw, whiteSpace: "nowrap", letterSpacing: 0.5 }}>
        {T.labels.axis}
      </div>
    </>
  );
};

const Marker: React.FC<{ T: Timing; frame: number }> = ({ T, frame }) => {
  const ld = T.ladder(frame);
  if (ld.vis <= 0) return null;
  const lf = T.driftFrame(T.loopFrame(frame));
  const breathe = 1 + 0.05 * Math.sin((lf / 40) * Math.PI * 2);
  const r = T.ladderInfo.markerR * breathe;
  const len = ld.streak * (10 + ld.L * 9);
  const streaks = [-7, -3, 0, 3, 7];
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
      {ld.streak > 0.02
        ? streaks.map((dx, i) => (
            <line key={i} x1={R.x + dx} y1={ld.y + 6 + Math.abs(dx) * 0.6} x2={R.x + dx} y2={ld.y + 6 + len * (1 - Math.abs(dx) / 12)} stroke={C.marker} strokeWidth={i === 2 ? 2.5 : 1.5}
              strokeLinecap="round" opacity={ld.streak * ld.vis * (0.55 - Math.abs(dx) * 0.04)} />
          ))
        : null}
      <circle cx={R.x} cy={ld.y} r={r * 3.2} fill={C.marker} opacity={0.12 * ld.vis} />
      <circle cx={R.x} cy={ld.y} r={r * 1.9} fill={C.marker} opacity={0.28 * ld.vis} />
      <circle cx={R.x} cy={ld.y} r={r} fill={C.marker} opacity={ld.vis} />
      <circle cx={R.x} cy={ld.y} r={r * 0.45} fill="#FFFFFF" opacity={0.9 * ld.vis} />
    </svg>
  );
};

export const Ladder: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  return (
    <>
      <Spine T={T} frame={frame} />
      <Rungs T={T} frame={frame} />
      <Marker T={T} frame={frame} />
    </>
  );
};
