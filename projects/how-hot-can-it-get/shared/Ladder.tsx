// THE LADDER RAIL (ROOT ONLY: Composition.tsx mounts <Ladder/> once; it reads props.rail / rungs / marks / zeros / glow
// through useT() and draws, on every frame):
//   the ICE FLOOR   a hairline at T.floorY(f) drawing left -> right on 'floor' (sc01), '0 K = -273.15 °C' SEATED on
//                   'absolute' (gravity drop, X7 tick ON the seat), 'the floor' with the hairline. NOT on the log axis
//                   (0 K is -infinity): a fixed callback below a break mark (art-direction 'the cold floor').
//   the SPINE       dashed Iron, x 180, drawing floor -> '?' on 'ceiling' (sc02); 'log scale' (rotated, left of the spine)
//                   from the first rung (sc03); decade ticks on the visible log range; above the Planck mark it FRAYS
//                   into a broken dash on 'breaks' (sc11) + 'where known physics stops working'.
//   the RUNGS       a tick per rung, dropping onto y = T.railY(L, f) ON its seat frame (T.seat); a rung that glows
//                   (>= the Draper point) is lit in its OWN black-body colour, Death Valley and Venus stay unlit Iron.
//                   COMPACT numbers (Saira Condensed 700 34 px) show while no window is open, from the end of the rung's
//                   intro scene (the unit's hero label owns the intro); the Planck rung shows 'Planck temperature'.
//   the MARKS       'first visible glow ~525 °C' (on 'hot', sc04), "Sun's surface ~5,500 °C" and 'colour barely changes
//                   past ~40,000 K' (each the frame the sc05 sweep passes it): a short dashed line + a label (labels thin
//                   out in the compressed views). All labels are de-overlapped bottom-up with leaders.
//   the CURSOR      a bead in the glow's colour riding the rail at log10(glow.k) during the sweep (sc05)
//   the '?'         the filament '?' (1,800 K) at L.q: draws on 'ceiling', dims to half on 'Planck', fades on 'ceiling' (s5)
//   the CHIPS       'black-body colour' (the live swatch, sc05 ->) and the ZEROS counter ('12 zeros' SEATED with the LHC
//                   rung -> '32 zeros' ON 'zeros', anchored under the active rung)
// Everything is a pure function of the frame (no state). Hooks at the top (lesson 1). No blend modes (lesson 24).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, E, FONT, L, rgba } from "../theme";
import { prog, useT } from "../time";
import type { Timing } from "../time";
import { DRAPER_K, bbRgb, lighten } from "./blackbody";
import { FilamentQ, QOutline } from "./FilamentStroke";
import { Rich } from "./Type";

const rgb = (c: [number, number, number], a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
const R = L.rail;
const COMPACT_PX = 34;
const MARK_PX = 24;
const LABEL_GAP = 40;

type Placed = { key: string; want: number; y: number; h: number; kind: "rung" | "mark" | "planck"; alpha: number };

/** de-overlap labels bottom-up: each sits at its wanted y or above the one below it (min gap), never above topY - 20 */
const deoverlap = (items: Placed[]) => {
  const s = [...items].sort((a, b) => b.want - a.want);
  let prev = Infinity;
  for (const it of s) {
    it.y = Math.min(it.want, prev - LABEL_GAP);
    prev = it.y;
  }
  return s;
};

const Spine: React.FC<{ T: Timing; frame: number }> = ({ T, frame }) => {
  const r = T.rail(frame);
  const floorY = T.floorY(frame);
  const topY = L.q.y + L.q.h / 2 + 8;
  // QA B3: the unlit spine is there (faint) from the opening; it DRAWS bright on 'ceiling' (spineStart)
  const faintA = 0.32 * prog(frame, 4, 24);
  if (r.spine <= 0)
    return (
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
        <line x1={R.x} y1={floorY} x2={R.x} y2={topY} stroke={C.ironLit} strokeWidth={2.5} strokeDasharray="10 7" opacity={faintA} />
      </svg>
    );
  const yTop = floorY - (floorY - topY) * r.spine;
  const planckY = T.railY(T.rung("planck").L, frame);
  const split = r.fray > 0 ? Math.max(yTop, Math.min(floorY, planckY)) : yTop;
  const lo = r.lo;
  const hiL = lo + (R.axisY0 - R.topY) / r.ppd;
  const ticks: number[] = [];
  for (let d = Math.ceil(lo); d <= Math.floor(hiL); d++) ticks.push(d);
  const tickA = prog(frame, T.sfx.windowOpen, T.sfx.windowOpen + 10);
  const breakY = R.floorY + r.camY - 36;
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
      {/* the faint unlit spine above the drawn part (until the draw completes) */}
      {r.spine < 1 ? <line x1={R.x} y1={yTop} x2={R.x} y2={topY} stroke={C.ironLit} strokeWidth={2.5} strokeDasharray="10 7" opacity={faintA} /> : null}
      {/* the spine, solid dashes below the Planck mark (or the whole drawn length) */}
      <line x1={R.x} y1={floorY} x2={R.x} y2={split} stroke={C.ironLit} strokeWidth={2.5} strokeDasharray="10 7" opacity={0.85} />
      {/* above the Planck mark: frays into a broken, fading dash on 'breaks' */}
      {r.fray > 0 && split > yTop ? (
        <line x1={R.x} y1={split} x2={R.x} y2={yTop} stroke={C.ash} strokeWidth={3.5}
          strokeDasharray={`${10 - 4 * r.fray} ${7 + 13 * r.fray} ${4} ${9 + 9 * r.fray}`} opacity={0.95 - 0.25 * r.fray} />
      ) : null}
      {/* the axis break between the floor callback and the log axis */}
      {r.spine > 0.1 ? (
        <path d={`M ${R.x - 10} ${breakY + 6} L ${R.x + 10} ${breakY - 2} M ${R.x - 10} ${breakY + 14} L ${R.x + 10} ${breakY + 6}`}
          stroke={C.ironLit} strokeWidth={2} opacity={0.8 * Math.min(1, r.spine * 3)} />
      ) : null}
      {/* decade ticks on the visible log range */}
      {tickA > 0
        ? ticks.map((d) => {
            const y = T.railY(d, frame);
            return y > yTop && y < R.axisY0 + r.camY + 1 ? <line key={d} x1={R.x - 7} y1={y} x2={R.x + 7} y2={y} stroke={C.ironLit} strokeWidth={2} opacity={0.7 * tickA} /> : null;
          })
        : null}
    </svg>
  );
};

const Floor: React.FC<{ T: Timing; frame: number }> = ({ T, frame }) => {
  const r = T.rail(frame);
  const y = T.floorY(frame);
  const x0 = 120;
  const x1 = x0 + (960 - x0) * r.floor;
  // ONE copy (no doubled text): dim from frame 0, it LIGHTS over 6 f and is fully lit ON 'absolute' (floorLabelSeat, X7)
  const lit = prog(frame, T.sfx.floorLabelSeat - 6, T.sfx.floorLabelSeat);
  const tagA = prog(frame, T.sfx.floorDraw + 8, T.sfx.floorDraw + 16);
  // QA B3: the floor (a dim ice hairline) and its labels (dim) are there from frame 0, larger; the hairline LIGHTS left -> right
  // on 'floor' (floorDraw) and '0 K = -273.15 °C' lights up, fully ON 'absolute' (X7 there)
  const VALUE_PX = 54;
  const valueTop = y - 76;
  const value = (opacity: number, dy: number, glow: boolean) => (
    <div style={{ position: "absolute", right: L.W - L.textRight, top: valueTop + dy, fontFamily: FONT.mono, fontWeight: 500, fontSize: VALUE_PX, lineHeight: 1.1,
      color: C.ice, opacity, whiteSpace: "nowrap", textShadow: glow ? `0 0 16px ${rgba(C.ice, 0.35)}` : "none" }}>
      {T.labels.floorValue}
    </div>
  );
  return (
    <>
      <div style={{ position: "absolute", left: x0, top: y - 1, width: 960 - x0, height: 2, backgroundColor: C.ice, opacity: 0.4 }} />
      {r.floor > 0 ? <div style={{ position: "absolute", left: x0, top: y - 1, width: x1 - x0, height: 2, backgroundColor: C.ice, boxShadow: `0 0 10px ${rgba(C.ice, 0.55)}` }} /> : null}
      <div style={{ position: "absolute", left: R.labelX, top: y - 44, fontFamily: FONT.mono, fontWeight: 400, fontSize: 30, color: C.ice, opacity: 0.55 + 0.3 * tagA, whiteSpace: "nowrap" }}>
        {T.labels.floor}
      </div>
      {value(0.5 + 0.5 * lit, 0, frame >= T.sfx.floorLabelSeat)}
    </>
  );
};

const Rungs: React.FC<{ T: Timing; frame: number }> = ({ T, frame }) => {
  const r = T.rail(frame);
  const placed: Placed[] = [];
  const ticks: React.ReactNode[] = [];
  for (const g of T.rungs) {
    const s = T.seat(frame, g.seat, 8, 18);
    if (!s.visible) continue;
    const y = T.railY(g.L, frame) + s.y;
    const c = g.glows ? bbRgb(g.kelvin) : null;
    ticks.push(
      <div key={g.id} style={{ position: "absolute", left: R.tickX0, top: y - 2.5, width: R.tickX1 - R.tickX0, height: 5, borderRadius: 3, opacity: s.opacity,
        backgroundColor: c ? rgb(lighten(c, 0.25)) : C.ironLit, boxShadow: c ? `0 0 14px ${rgb(c, 0.9)}, 0 0 4px ${rgb(c)}` : "none" }} />,
    );
    if (g.id === "planck") {
      const a = prog(frame, g.seat - 8, g.seat); // lesson 31: fully visible ON its seat (tick + X3 land there)
      if (a > 0) placed.push({ key: g.id, want: T.railY(g.L, frame), y: 0, h: 30, kind: "planck", alpha: a });
    } else if (frame >= g.compactFrom) {
      const a = r.compactVis * prog(frame, g.compactFrom - 8, g.compactFrom);
      if (a > 0.001) placed.push({ key: g.id, want: T.railY(g.L, frame), y: 0, h: 38, kind: "rung", alpha: a });
    }
  }
  const markA = Math.max(0, Math.min(1, (r.ppd - 40) / 30));
  const marks: React.ReactNode[] = [];
  for (const m of T.marks) {
    if (frame <= m.at - 8) continue;
    const a = prog(frame, m.at - 8, m.at); // lesson 31: fully visible ON its frame
    const y = T.railY(m.L, frame);
    marks.push(<div key={m.id} style={{ position: "absolute", left: R.x - 16, top: y - 1, width: 52, height: 0, borderTop: `2px dashed ${rgba(C.ash, 0.9)}`, opacity: a }} />);
    // QA B5: a mark label shows only in the clear (no plate up: compactVis is 0 while a plate is more than ~1/3 visible);
    // the Draper mark's label is introduced over the Venus plate and stays through its close
    const winA = m.id === "draper" && frame < T.sfx.windowOpen2 ? 1 : r.compactVis;
    if (markA > 0 && winA > 0) placed.push({ key: m.id, want: y, y: 0, h: 30, kind: "mark", alpha: a * markA * winA });
  }
  const laid = deoverlap(placed);
  return (
    <>
      {marks}
      {ticks}
      {laid.map((p) => {
        const lead = Math.abs(p.y - p.want) > 3;
        const leader = lead ? (
          <svg key={`l-${p.key}`} width={40} height={Math.abs(p.y - p.want) + 4} style={{ position: "absolute", left: R.tickX1 - 2, top: Math.min(p.y, p.want) - 2, overflow: "visible" }}>
            <path d={`M 0 ${p.want > p.y ? Math.abs(p.y - p.want) + 2 : 2} L ${10} ${p.want > p.y ? 2 : Math.abs(p.y - p.want) + 2}`} stroke={rgba(C.ash, 0.7)} strokeWidth={1.5} fill="none" opacity={p.alpha} />
          </svg>
        ) : null;
        if (p.kind === "rung") {
          const g = T.rung(p.key as never);
          return (
            <React.Fragment key={p.key}>
              {leader}
              <div style={{ position: "absolute", left: R.labelX, top: p.y - COMPACT_PX * 0.62, fontFamily: FONT.display, fontWeight: 700, fontSize: COMPACT_PX, lineHeight: 1.2,
                color: C.bone, opacity: 0.92 * p.alpha, whiteSpace: "nowrap", textShadow: "0 2px 10px rgba(11,9,7,0.85)" }}>
                <Rich text={g.num} size={COMPACT_PX} />
              </div>
            </React.Fragment>
          );
        }
        const text = p.kind === "planck" ? T.labels.planck : T.mark(p.key as never).text;
        return (
          <React.Fragment key={p.key}>
            {leader}
            <div style={{ position: "absolute", left: R.labelX + 6, top: p.y - MARK_PX * 0.7, fontFamily: FONT.mono, fontWeight: p.kind === "planck" ? 500 : 400,
              fontSize: p.kind === "planck" ? 26 : MARK_PX, lineHeight: 1.2, color: p.kind === "planck" ? C.bone : C.ash, opacity: p.alpha, whiteSpace: "nowrap",
              padding: "0 6px", backgroundColor: rgba(C.forge, 0.62), borderRadius: 4 }}>
              <Rich text={text} size={p.kind === "planck" ? 26 : MARK_PX} />
            </div>
          </React.Fragment>
        );
      })}
    </>
  );
};

const Chips: React.FC<{ T: Timing; frame: number }> = ({ T, frame }) => {
  const r = T.rail(frame);
  const g = T.glow(frame);
  const z = T.zeros(frame);
  const out: React.ReactNode[] = [];
  if (r.chip > 0) {
    const sw = r.chip;
    out.push(
      <div key="bb" style={{ position: "absolute", left: L.chip.x, top: L.chip.y, height: L.chip.h, display: "flex", alignItems: "center", gap: 12, padding: "0 14px 0 8px",
        borderRadius: L.chip.h / 2, backgroundColor: rgba(C.forge, 0.72), border: `1.5px solid ${rgba(C.ironLit, 0.9)}`, opacity: sw }}>
        {g.k < DRAPER_K ? (
          <div style={{ width: 28, height: 28, borderRadius: 14, backgroundColor: C.iron, border: `2px solid ${C.ironLit}`, boxSizing: "border-box" }} />
        ) : (
          <div style={{ width: 28, height: 28, borderRadius: 14, backgroundColor: g.css(1), boxShadow: `0 0 14px ${g.css(0.85)}` }} />
        )}
        <span style={{ fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.bone, whiteSpace: "nowrap" }}>{T.labels.chip}</span>
      </div>,
    );
  }
  if (z.alpha > 0) {
    const s = T.seat(frame, T.sfx.lhcSeat, 8, 14);
    const y = T.railY(z.L, frame) + 40 + (frame < T.sfx.lhcSeat ? s.y : 0);
    out.push(
      <div key="zeros" style={{ position: "absolute", left: R.labelX, top: y - 21, height: 42, display: "flex", alignItems: "center", padding: "0 14px",
        borderRadius: 8, backgroundColor: rgba(C.forge, 0.8), border: `1.5px solid ${rgba(C.ironLit, 0.95)}`, opacity: z.alpha,
        fontFamily: FONT.mono, fontWeight: 500, fontSize: 30, color: C.bone, whiteSpace: "nowrap", fontVariantNumeric: "tabular-nums" }}>
        {`${z.value} ${T.labels.zerosUnit}`}
      </div>,
    );
  }
  return <>{out}</>;
};

export const Ladder: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const r = T.rail(frame);
  const g = T.glow(frame);
  const logA = prog(frame, T.sfx.windowOpen, T.sfx.windowOpen + 10);
  const planckY = T.railY(T.rung("planck").L, frame);
  const frayA = prog(frame, T.sfx.fray - 6, T.sfx.fray, E.calm);
  const curY = T.railY(Math.log10(g.k), frame);
  return (
    <>
      <Spine T={T} frame={frame} />
      <Floor T={T} frame={frame} />
      {logA > 0 ? (
        <div style={{ position: "absolute", left: R.x - 34, top: 700 + r.camY, transform: "translate(-50%, -50%) rotate(-90deg)", fontFamily: FONT.mono, fontWeight: 400,
          fontSize: 24, color: C.ash, opacity: 0.85 * logA, whiteSpace: "nowrap", letterSpacing: 1 }}>
          {T.labels.logScale}
        </div>
      ) : null}
      <Rungs T={T} frame={frame} />
      {r.cursor > 0 ? (
        // HONESTY: the bead is UNLIT Iron while the displayed temperature is below the Draper point (nothing that cool
        // glows: no red beside the Venus value); from ~525 degC it takes the computed black-body colour
        g.k < DRAPER_K ? (
          <div style={{ position: "absolute", left: R.x - 9, top: curY - 9, width: 18, height: 18, borderRadius: 9, opacity: r.cursor,
            backgroundColor: C.iron, border: `2px solid ${C.ironLit}` }} />
        ) : (
          <div style={{ position: "absolute", left: R.x - 10, top: curY - 10, width: 20, height: 20, borderRadius: 10, opacity: r.cursor,
            backgroundColor: rgb(lighten(g.rgb, 0.5).map((v) => Math.round(v * g.lum)) as [number, number, number]), boxShadow: `0 0 18px ${g.css(1)}, 0 0 40px ${g.css(0.7)}` }} />
        )
      ) : null}
      {/* QA B3: the UNLIT iron-grey '?' outline waits at the top from ~f10-30; it ignites on 'ceiling' (the filament draws over it) */}
      {r.qAlpha > 0 ? <QOutline x={L.q.x} y={L.q.y} h={L.q.h} opacity={0.6 * prog(frame, 10, 30) * r.qAlpha} /> : null}
      {r.q > 0 && r.qAlpha > 0 ? <FilamentQ x={L.q.x} y={L.q.y} h={L.q.h} q={r.q} kelvin={T.railInfo.qK} opacity={r.qAlpha} /> : null}
      {frayA > 0 ? (
        <div style={{ position: "absolute", left: R.labelX + 6, top: planckY - 62, fontFamily: FONT.mono, fontWeight: 500, fontSize: 25, color: C.bone, opacity: 0.85 * frayA,
          whiteSpace: "nowrap", padding: "1px 8px", backgroundColor: rgba(C.forge, 0.78), borderRadius: 4 }}>
          {T.labels.fray}
        </div>
      ) : null}
      <Chips T={T} frame={frame} />
    </>
  );
};
