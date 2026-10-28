// THE SCALE WELL RAIL (ROOT ONLY: Composition.tsx mounts <Ladder/> once; it reads props.ladder / props.devices.refs through
// useT() and draws, on every frame). Video 16's ladder flipped DOWNWARD in metres:
//   the RAIL       a steel spine at x 250, L = -log10(m): L 3 (1 mm) at y 380 down to L 18 (10^-18 m) at y 1000; dim from
//                  frame 0, DRAWS bright top -> bottom from railDraw (X1); decade ticks x 236-264 with their powers ('10⁻³ m'
//                  ... '10⁻¹⁸ m', IBM Plex Mono 28 px, the exponent DRAWN raised by <Sci>), right-aligned at x 224;
//                  'metres · log scale' above the rail's top.
//   REF LINES      'YOUR EYE · ~0.1 mm' (L 4.0, eyeLine) and 'LIGHT MICROSCOPE · ~200 nm' (L 6.70, lightLine): dashed steel
//                  lines across the rail, drawn ON their key frames; their labels sit LEFT of the rail (the decade power
//                  under a label is hidden); the eye carries a small eye icon; from the eye line down, a faint VEIL dims the rail.
//   the RUNGS      a tick per rung dropping onto y = railY(L) ON its seat (T.seat) WITH its label chip (name Saira 700 28 px +
//                  number IBM Plex Mono 500 28 px; two lines when one would reach under the open window). Chips de-overlap
//                  TOP-DOWN with thin leaders (build_props.py mirrors the layout and asserts it).
//   the MARKER     the warm white-amber bead (r 6 + glow) at railY(markerL), breathing on the loop clock (still from the release).
// Pure function of the frame. Hooks at the top (lesson 1). No blend modes (lesson 24).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { useT } from "../time";
import type { Timing } from "../time";
import type { Rung } from "../types";
import { Rich, Sci, measure } from "./Type";

const R = L.rail;
const LABEL_PX = 28;
const CHIP_PAD = 12;
const ROW_H = 36;
const CHIP_GAP = 6;
const SUPD = "⁰¹²³⁴⁵⁶⁷⁸⁹";
const DECADES = Array.from({ length: R.L1 - R.L0 + 1 }, (_, i) => {
  const n = R.L0 + i;
  return { L: n, text: `10⁻${String(n).split("").map((d) => SUPD[Number(d)]).join("")} m` };
});
const REF_HALF = 25; // a reference label's half height (two 24 px rows around its line)

type Placed = { rung: Rung; want: number; y: number; h: number; w: number; drop: number; alpha: number };

const chipHeight = (r: Rung) => r.lines.length * ROW_H + 8;
const chipWidth = (r: Rung) => {
  let w = 0;
  for (const line of r.lines) {
    if (line.includes(" · ")) {
      const [name, num] = line.split(" · ");
      w = Math.max(w, measure(name, "display", LABEL_PX) + measure(" · ", "display", LABEL_PX) + measure(num, "monoMed", LABEL_PX));
    } else w = Math.max(w, line === r.num ? measure(line, "monoMed", LABEL_PX) : measure(line, "display", LABEL_PX));
  }
  return w + 2 * CHIP_PAD;
};

/** de-overlap TOP-DOWN: each chip sits at its wanted y or just below the one above it (the ladder runs downward) */
const deoverlap = (items: Placed[]) => {
  const s = [...items].sort((a, b) => a.want - b.want);
  let prevBottom = -Infinity;
  for (const it of s) {
    it.y = Math.max(it.want, prevBottom + CHIP_GAP + it.h / 2);
    prevBottom = it.y + it.h / 2;
  }
  return s;
};

const Line: React.FC<{ line: string; num: string }> = ({ line, num }) => {
  if (line.includes(" · ")) {
    const [name, n] = line.split(" · ");
    return (
      <span style={{ whiteSpace: "nowrap" }}>
        <span style={{ fontFamily: FONT.display, fontWeight: 700 }}>{name}</span>
        <span style={{ fontFamily: FONT.display, fontWeight: 700, color: C.steel }}> · </span>
        <span style={{ fontFamily: FONT.mono, fontWeight: 500 }}><Rich text={n} size={LABEL_PX} /></span>
      </span>
    );
  }
  const isNum = line === num;
  return (
    <span style={{ fontFamily: isNum ? FONT.mono : FONT.display, fontWeight: isNum ? 500 : 700, whiteSpace: "nowrap" }}>
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
              backgroundColor: rgba(C.chip, 0.9), border: `1px solid ${rgba(C.steel, 0.35)}`, opacity: p.alpha, color: C.bone, fontSize: LABEL_PX, lineHeight: `${ROW_H}px` }}>
              {p.rung.lines.map((line, i) => (
                <div key={i} style={{ height: ROW_H }}><Line line={line} num={p.rung.num} /></div>
              ))}
            </div>
          </React.Fragment>
        );
      })}
    </>
  );
};

/** a small drawn eye (almond + iris), centred on (x, y) */
const EyeIcon: React.FC<{ x: number; y: number; w: number; opacity: number }> = ({ x, y, w, opacity }) => {
  const h = w * 0.55;
  return (
    <svg width={w + 4} height={h + 4} style={{ position: "absolute", left: x - w / 2 - 2, top: y - h / 2 - 2, opacity }}>
      <path d={`M 2 ${h / 2 + 2} Q ${w / 2 + 2} ${-h * 0.35} ${w + 2} ${h / 2 + 2} Q ${w / 2 + 2} ${h * 1.35 + 2} 2 ${h / 2 + 2} Z`} fill="none" stroke={C.steel} strokeWidth={2} />
      <circle cx={w / 2 + 2} cy={h / 2 + 2} r={h * 0.3} fill={C.steel} />
    </svg>
  );
};

const Spine: React.FC<{ T: Timing; frame: number }> = ({ T, frame }) => {
  const ld = T.ladder(frame);
  const drawn = R.y0 + (R.y1 - R.y0) * ld.railDraw;
  const refs = T.dev.refs.map((r) => ({ r, y: T.railY(r.L), d: T.ch(r.draw, frame) }));
  const eyeY = T.railY(T.dev.refs[0].L);
  return (
    <>
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
        {/* the dim rail from frame 0, the bright one drawing over it top -> bottom */}
        <line x1={R.x} y1={R.y0} x2={R.x} y2={R.y1} stroke={C.steelDim} strokeWidth={3} opacity={0.55} />
        {ld.railDraw > 0 ? <line x1={R.x} y1={R.y0} x2={R.x} y2={drawn} stroke={C.steel} strokeWidth={3} opacity={0.9} /> : null}
        {DECADES.map((d) => {
          const y = T.railY(d.L);
          return <line key={d.L} x1={R.tickX0} y1={y} x2={R.tickX1} y2={y} stroke={C.steelDim} strokeWidth={2} opacity={y <= drawn ? 0.85 : 0.4} />;
        })}
      </svg>
      {DECADES.map((d) => {
        const y = T.railY(d.L);
        const hidden = refs.reduce((m, x) => Math.max(m, y - x.y > -REF_HALF - 6 && y - x.y < REF_HALF + 20 ? x.d : 0), 0);
        const a = (y <= drawn ? 0.85 : 0.4) * (1 - hidden);
        if (a <= 0) return null;
        return (
          <div key={d.L} style={{ position: "absolute", right: L.W - R.numRight, top: y - 15, height: 30, fontFamily: FONT.mono, fontWeight: 400, fontSize: 28, lineHeight: "30px",
            color: C.steelDim, opacity: a, whiteSpace: "nowrap" }}>
            <Sci text={d.text} size={28} />
          </div>
        );
      })}
      <div style={{ position: "absolute", left: L.axisLabel.x, top: L.axisLabel.y - 14, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "28px", color: C.steel,
        opacity: 0.55 + 0.35 * ld.railDraw, whiteSpace: "nowrap", letterSpacing: 0.5 }}>
        {T.labels.axis}
      </div>
      {/* THE VEIL: below your eye, the rail dims (from eyeLine, for the rest of the film) */}
      {ld.veil > 0 ? (
        <div style={{ position: "absolute", left: 40, top: eyeY + 2, width: R.rungX1 + 6 - 40, height: R.planckY + 10 - eyeY, backgroundColor: rgba(C.skyBottom, ld.veil) }} />
      ) : null}
      {/* REFERENCE LINES (dashed, not rungs) + their labels left of the rail */}
      {refs.map(({ r, y, d }) =>
        d <= 0 ? null : (
          <React.Fragment key={r.id}>
            <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
              <line x1={R.tickX0 - 6} y1={y} x2={R.tickX0 - 6 + (R.labelX + 292 - R.tickX0 + 6) * d} y2={y} stroke={C.steel} strokeWidth={2} strokeDasharray="8 7" opacity={0.75} />
            </svg>
            <div style={{ position: "absolute", right: L.W - R.numRight, top: y - REF_HALF, height: 2 * REF_HALF, display: "flex", flexDirection: "column", alignItems: "flex-end",
              justifyContent: "space-between", opacity: Math.min(1, d * 1.5), color: C.bone, whiteSpace: "nowrap" }}>
              <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 26, lineHeight: "24px" }}>{r.lines[0]}</div>
              <div style={{ fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "24px", color: C.steel }}><Rich text={r.lines[1]} size={24} /></div>
            </div>
            {r.id === "eye" ? <EyeIcon x={R.numRight - measure(r.lines[0], "display", 26) - 26} y={y - REF_HALF + 12} w={30} opacity={Math.min(1, d * 1.5)} /> : null}
          </React.Fragment>
        ),
      )}
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
