// THE WEIGHT COLUMN RAIL (ROOT ONLY: Composition.tsx mounts <Ladder/> once; it reads props.ladder through useT() and draws, on
// every frame). Video 17's ladder pointing UP in kilograms:
//   the RAIL       a steel spine at x 250, L = log10(kg): L 0 (1 kg) at y 1000 up to L 37 at y 380; dim from frame 0, DRAWS
//                  bright bottom -> top from railDraw; ticks every 3 powers x 236-264 with their powers ('10⁰ kg' ... '10³⁶ kg',
//                  IBM Plex Mono 28 px, the exponent DRAWN raised by <Sci>), right-aligned at x 224; 'kilograms · log scale'
//                  under the rail's bottom.
//   the RUNGS      a tick per rung dropping onto y = railY(L) ON its seat (T.seat) WITH its label chip (name Saira 700 28 px +
//                  number IBM Plex Mono 500 26 px; one line, or the name over the number (split once more when it would reach
//                  under the open window)). Chips de-overlap BOTTOM-UP with thin leaders (the ladder climbs: a new chip never
//                  shoves a seated one; build_props.py mirrors the layout and asserts it).
//   the MARKER     the heavy bronze-white bead (r 7 + glow) at railY(markerL), breathing on the loop clock (still from the
//                  release); a ghost (~0.3) from universeIn.
// Pure function of the frame. Hooks at the top (lesson 1). No blend modes (lesson 24).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { useT } from "../time";
import type { Timing } from "../time";
import type { Rung } from "../types";
import { Sci, measure } from "./Type";

const R = L.rail;
const NAME_PX = 28;
const NUM_PX = 26;
const CHIP_PAD = 12;
const ROW_H = 30;
const CHIP_GAP = 6;
const SUPD = "⁰¹²³⁴⁵⁶⁷⁸⁹";
const DECADES = Array.from({ length: Math.floor((R.L1 - R.L0) / 3) + 1 }, (_, i) => {
  const n = R.L0 + 3 * i;
  return { L: n, text: `10${String(n).split("").map((d) => SUPD[Number(d)]).join("")} kg` };
});

type Placed = { rung: Rung; want: number; y: number; h: number; w: number; drop: number; alpha: number };

const chipHeight = (r: Rung) => r.lines.length * ROW_H + 8;
const lineWidth = (r: Rung, line: string) => {
  if (line.startsWith(`${r.name} · `)) return measure(r.name, "display", NAME_PX) + measure(" · ", "display", NAME_PX) + measure(line.slice(r.name.length + 3), "monoMed", NUM_PX);
  return line === r.name ? measure(line, "display", NAME_PX) : measure(line, "monoMed", NUM_PX);
};
const chipWidth = (r: Rung) => Math.max(...r.lines.map((l) => lineWidth(r, l))) + 2 * CHIP_PAD;

/** de-overlap BOTTOM-UP: each chip sits at its wanted y or just above the one below it (the ladder climbs) */
const deoverlap = (items: Placed[]) => {
  const s = [...items].sort((a, b) => b.want - a.want);
  let prevTop = Infinity;
  for (const it of s) {
    it.y = Math.min(it.want, prevTop - CHIP_GAP - it.h / 2);
    prevTop = it.y - it.h / 2;
  }
  return s;
};

const Line: React.FC<{ line: string; r: Rung }> = ({ line, r }) => {
  if (line.startsWith(`${r.name} · `)) {
    return (
      <span style={{ whiteSpace: "nowrap" }}>
        <span style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: NAME_PX }}>{r.name}</span>
        <span style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: NAME_PX, color: C.steel }}> · </span>
        <span style={{ fontFamily: FONT.mono, fontWeight: 500, fontSize: NUM_PX }}><Sci text={line.slice(r.name.length + 3)} size={NUM_PX} /></span>
      </span>
    );
  }
  const isName = line === r.name;
  return (
    <span style={{ fontFamily: isName ? FONT.display : FONT.mono, fontWeight: isName ? 700 : 500, fontSize: isName ? NAME_PX : NUM_PX, whiteSpace: "nowrap" }}>
      <Sci text={line} size={isName ? NAME_PX : NUM_PX} />
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
        const d = p.y - p.want;
        const lead = Math.abs(d) > 3;
        const top = p.y - p.h / 2 + p.drop;
        return (
          <React.Fragment key={p.rung.id}>
            {lead ? (
              <svg width={R.labelX - R.rungX1 + 2} height={Math.abs(d) + 6} style={{ position: "absolute", left: R.rungX1 - 1, top: Math.min(p.y, p.want) - 3 + p.drop, overflow: "visible", opacity: p.alpha }}>
                <path d={`M 0 ${d > 0 ? 3 : Math.abs(d) + 3} L ${R.labelX - R.rungX1} ${d > 0 ? Math.abs(d) + 3 : 3}`} stroke={rgba(C.steel, 0.6)} strokeWidth={1.5} fill="none" />
              </svg>
            ) : null}
            <div style={{ position: "absolute", left: R.labelX, top, width: p.w, height: p.h, boxSizing: "border-box", padding: `4px ${CHIP_PAD}px`, borderRadius: 10,
              backgroundColor: rgba(C.chip, 0.9), border: `1px solid ${rgba(C.steel, 0.35)}`, opacity: p.alpha, color: C.bone, lineHeight: `${ROW_H}px` }}>
              {p.rung.lines.map((line, i) => (
                <div key={i} style={{ height: ROW_H }}><Line line={line} r={p.rung} /></div>
              ))}
            </div>
          </React.Fragment>
        );
      })}
    </>
  );
};

const Spine: React.FC<{ T: Timing; frame: number }> = ({ T, frame }) => {
  const ld = T.ladder(frame);
  const drawn = R.y1 - (R.y1 - R.y0) * ld.railDraw;
  return (
    <>
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
        {/* the dim rail from frame 0, the bright one drawing over it bottom -> top */}
        <line x1={R.x} y1={R.y0} x2={R.x} y2={R.y1} stroke={C.steelDim} strokeWidth={3} opacity={0.55} />
        {ld.railDraw > 0 ? <line x1={R.x} y1={R.y1} x2={R.x} y2={drawn} stroke={C.steel} strokeWidth={3} opacity={0.9} /> : null}
        {DECADES.map((d) => {
          const y = T.railY(d.L);
          return <line key={d.L} x1={R.tickX0} y1={y} x2={R.tickX1} y2={y} stroke={C.steelDim} strokeWidth={2} opacity={y >= drawn ? 0.85 : 0.4} />;
        })}
      </svg>
      {DECADES.map((d) => {
        const y = T.railY(d.L);
        return (
          <div key={d.L} style={{ position: "absolute", right: L.W - R.numRight, top: y - 15, height: 30, fontFamily: FONT.mono, fontWeight: 400, fontSize: 28, lineHeight: "30px",
            color: C.steelDim, opacity: y >= drawn ? 0.85 : 0.4, whiteSpace: "nowrap" }}>
            <Sci text={d.text} size={28} />
          </div>
        );
      })}
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
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
      <circle cx={R.x} cy={ld.y} r={r * 3.0} fill={C.marker} opacity={0.12 * ld.vis} />
      <circle cx={R.x} cy={ld.y} r={r * 1.8} fill={C.marker} opacity={0.3 * ld.vis} />
      <circle cx={R.x} cy={ld.y} r={r} fill={C.marker} opacity={ld.vis} />
      <circle cx={R.x} cy={ld.y} r={r * 0.45} fill="#FFF6EA" opacity={0.9 * ld.vis} />
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
