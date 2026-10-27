// U2's ONE continuous stage (sc07-sc12, frames 651-1360; BUILD.md §7). Every U2 scene file mounts <U2Picture/> and its
// Overlay mounts <U2Overlay/>: each element below is gated by its own key frames, so the unit-internal seams (722, 835, 1007,
// 1133, 1245) match by construction and the ledger is ONE component with the same props on both sides of 1245.
//   sc07  the skater inset (right column, its own 'drawn · not to scale' tag), arms in ON armsIn; 'smaller → spins faster'
//         from armsIn; all of it gone by sc07's end (722) - before the swap's tab pulse (724)
//   sc08  roll arcs hugging each half while the BACK half follows (backTurnStart -> swapEnd): cyan on the back half, a small
//         amber one on the front half the other way; gone by 812
//   sc09  the roll axes fade with 'Legs out'; contact marks at the paws ON land (936, X6) - nothing on 935
//   sc10  'NOT ALWAYS' seated ON stampNotAlways (X3, overlay, across the card), out by 1133; 'short drop: no time to turn'
//         (PROBABLY grammar) under the floor line from the ghost's first visible frame, out with it by shortGone
//   sc11  the ledger seated ON ledgerSeat (X7), the bar barFrom -> barTo with '~90% survived'
//   sc12  ghost column ON ghostColumn, 'not counted' ON notCounted, bracket 'of cats brought in' ON bracket; all constant
//         long before vetEndFrame (1314), so the settle is still
// The cat and the dials are ONLY the curves (<CatLive/>, <DialsLive/>); nothing here moves or redraws the cat.
// Hooks at the top of each component, before any early return (lesson 1). Pure per-frame maths (deterministic).

import React from "react";
import { useCurrentFrame } from "remotion";
import { CAT, CatLive } from "../../shared/Cat";
import { DialsLive } from "../../shared/Dials";
import { ArrowLabel, CurvedArrow } from "../../shared/Icons";
import { Ledger } from "../../shared/Ledger";
import { Skater as SkaterFigure } from "../../shared/Skater";
import { Stamp } from "../../shared/Stamp";
import { Label } from "../../shared/Type";
import { WindowFrame } from "../../shared/Window";
import { SceneTag } from "../../overlay/Tag";
import { C, E, L, rgba } from "../../theme";
import { prog, useT } from "../../time";
import type { Timing } from "../../time";

const SKATER_LABEL = "smaller → spins faster";
const STAMP_TEXT = "NOT ALWAYS";
const SHORT_LABEL = "short drop: no time to turn";
const TITLE_TEXT = "1987 · Animal Medical Center, NY";
const ROW_TEXT = "132 cats · high-rise falls";
const BAR_LABEL = "~90% survived";
const GHOST_LABEL = "never reached a vet";
const NOT_COUNTED_LABEL = "not counted";
const BRACKET_LABEL = "of cats brought in";

/** the skater inset box (right column, under the dials) and its tag row */
const INSET = { x0: 648, x1: 912, y0: 874, y1: 1050 };
const INSET_FADE = 8;

const rad = (d: number) => (d * Math.PI) / 180;

/** the skater inset's visibility: in from sc07's first frame, out over INSET_FADE frames ending ON sc07's end */
const insetVis = (T: Timing, f: number) => {
  const sc = T.scene("sc07");
  if (f < sc.from || f >= sc.to) return 0;
  return prog(f, sc.from - 1, sc.from + 5) * (1 - prog(f, sc.to - INSET_FADE, sc.to));
};
/** arms 0 (out) -> 1 (in), fully in ON armsIn */
const armsAt = (T: Timing, f: number) => prog(f, T.sfx.armsIn - 10, T.sfx.armsIn, E.calm);

/** sc08 roll arcs: visible while the back half follows, out by swapEnd + 17 */
const arcVis = (T: Timing, f: number) =>
  f <= T.sfx.backTurnStart ? 0 : prog(f, T.sfx.backTurnStart, T.sfx.backTurnStart + 4) * (1 - prog(f, T.sfx.swapEnd + 5, T.sfx.swapEnd + 17));

/** a roll arc around one half's long axis (seen from the side: an upright ellipse), drawn `turn` radians from the top */
const RollArc: React.FC<{ cx: number; rx: number; ry: number; turn: number; color: string }> = ({ cx, rx, ry, turn, color }) => {
  if (Math.abs(turn) < 0.05) return null;
  const n = 28;
  const pts: string[] = [];
  for (let i = 0; i <= n; i++) {
    const t = (turn * i) / n;
    pts.push(`${i === 0 ? "M" : "L"} ${(cx + rx * Math.sin(t)).toFixed(2)} ${(-ry * Math.cos(t)).toFixed(2)}`);
  }
  const hx = cx + rx * Math.sin(turn), hy = -ry * Math.cos(turn);
  const s = Math.sign(turn);
  const ha = Math.atan2(s * ry * Math.sin(turn), s * rx * Math.cos(turn));
  const d = pts.join(" ");
  return (
    <g>
      <CurvedArrow d={d} hx={hx} hy={hy} ha={ha} color={rgba(C.shadow, 0.75)} width={9} head={15} />
      <CurvedArrow d={d} hx={hx} hy={hy} ha={ha} color={color} width={5} head={14} />
    </g>
  );
};

/** the paws' contact x positions (from the curves at the landing frame): one per leg pair, at the floor line */
const contactXs = (T: Timing) => {
  const p = T.cat(T.sfx.land);
  const b = p.bend / 2 - p.arch * 7;
  const xs: number[] = [];
  for (const which of ["front", "back"] as const) {
    const dir = which === "front" ? -1 : 1;
    const th = rad(which === "front" ? b : -b);
    const by = -Math.cos(rad(which === "front" ? p.front : p.back));
    const out = CAT.legOut * (1 - 0.25 * p.flex) - 7.5;
    const lx = dir * CAT.halfLen * 0.7 - dir * 6; // between the near and far paws
    const ly = by * (CAT.halfH - 7.5) + by * out * Math.max(0.18, Math.abs(by));
    xs.push(p.x + p.scale * (lx * Math.cos(th) - ly * Math.sin(th)));
  }
  return xs;
};
const CONTACT_F = 13;

export const U2Picture: React.FC = () => {
  const f = useCurrentFrame();
  const T = useT();
  const pose = T.cat(f);
  const sc07 = T.scene("sc07");
  const sc10 = T.scene("sc10");
  // the dashed roll axes: on from the 651 seam (U1 shows them at 650), out with 'Legs out' (sc09)
  const axes = 1 - prog(f, T.sfx.tick05 - 10, T.sfx.tick05, E.calm);
  // sc07 skater
  const iv = insetVis(T, f);
  let phase = 0;
  if (iv > 0) for (let g = sc07.from; g < f; g++) phase += 0.1 + 0.42 * armsAt(T, g);
  const labelOp = f >= T.sfx.armsIn && f < sc07.to ? 1 - prog(f, sc07.to - INSET_FADE, sc07.to) : 0;
  // sc08 roll arcs (each hugs its own half; the back half's arc follows its turn, the front's goes the other way, smaller)
  const av = arcVis(T, f);
  const bHalf = pose.bend / 2 - pose.arch * 7;
  const backTurn = Math.max(0, Math.min(1, (pose.back + 20) / 200)) * rad(300);
  const frontTurn = -Math.max(0, Math.min(1, (200 - pose.front) / 20)) * rad(110);
  // sc09 contact marks: ON land, gone before the S2 window
  const cOn = f >= T.sfx.land && f < T.sfx.land + CONTACT_F;
  const ck = prog(f, T.sfx.land - 1, T.sfx.land + 6, E.open);
  const cOp = 1 - prog(f, T.sfx.land + 4, T.sfx.land + CONTACT_F);
  const floorY = T.rig(f).floorY;
  // sc11-sc12 the ledger (one component across the 1245 seam)
  const seat = T.seat(f, T.sfx.ledgerSeat, T.motion.SEAT_F, 40);
  const showCat = f < sc10.to;
  return (
    <>
      {showCat ? <CatLive axes={axes} /> : null}
      {showCat ? <DialsLive /> : null}
      {av > 0 || cOn ? (
        <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
          {av > 0 ? (
            <g opacity={av} transform={`translate(${pose.x} ${pose.y}) scale(${pose.scale})`}>
              <g transform={`rotate(${-bHalf})`}>
                <RollArc cx={CAT.halfLen * 0.55} rx={24} ry={CAT.halfH + 30} turn={backTurn} color={C.back} />
              </g>
              <g transform={`rotate(${bHalf})`}>
                <RollArc cx={-CAT.halfLen * 0.55} rx={18} ry={CAT.halfH + 22} turn={frontTurn} color={C.front} />
              </g>
            </g>
          ) : null}
          {cOn
            ? contactXs(T).map((x, i) => (
                <g key={i} opacity={cOp} stroke={C.steelLit} strokeWidth={4} strokeLinecap="round" fill="none">
                  {[-1, 1].map((s) => (
                    <g key={s}>
                      <path d={`M ${x + s * (16 + 10 * ck)} ${floorY - 2} L ${x + s * (34 + 22 * ck)} ${floorY - 2}`} />
                      <path d={`M ${x + s * (14 + 8 * ck)} ${floorY - 10} L ${x + s * (26 + 18 * ck)} ${floorY - 24 - 10 * ck}`} />
                    </g>
                  ))}
                </g>
              ))
            : null}
        </svg>
      ) : null}
      {iv > 0 ? (
        <div style={{ position: "absolute", inset: 0, opacity: iv }}>
          <WindowFrame box={INSET} open={1} radius={16} frame={4}>
            <div style={{ position: "absolute", inset: 0, backgroundColor: C.drapeDeep }} />
            <svg width={INSET.x1 - INSET.x0} height={INSET.y1 - INSET.y0} style={{ position: "absolute", inset: 0 }}>
              <SkaterFigure x={(INSET.x1 - INSET.x0) / 2} y={104} arms={armsAt(T, f)} phase={phase} scale={0.78} />
            </svg>
          </WindowFrame>
        </div>
      ) : null}
      {labelOp > 0 ? <ArrowLabel x={140} y={(INSET.y0 + INSET.y1) / 2} text={SKATER_LABEL} size={30} opacity={labelOp} /> : null}
      {seat.k > 0 ? (
        <Ledger k={seat.k} dropY={seat.y} title={TITLE_TEXT} rows={[ROW_TEXT]} bar={prog(f, T.sfx.barFrom - 1, T.sfx.barTo)} barLabel={BAR_LABEL}
          ghost={prog(f, T.sfx.ghostColumn - 1, T.sfx.ghostColumn + 13, E.calm)} ghostHeader={GHOST_LABEL}
          notCounted={prog(f, T.sfx.notCounted - 1, T.sfx.notCounted + 5)} notCountedText={NOT_COUNTED_LABEL}
          bracket={prog(f, T.sfx.bracket - 1, T.sfx.bracket + 7)} bracketText={BRACKET_LABEL} />
      ) : null}
    </>
  );
};

export const U2Overlay: React.FC = () => {
  const f = useCurrentFrame();
  const T = useT();
  const sc07 = T.scene("sc07");
  const sc10 = T.scene("sc10");
  // 'NOT ALWAYS': fully down ON stampNotAlways (X3), across the completed card; out over 8 f ending ON sc10's end (< 1135)
  const st = T.seat(f, T.sfx.stampNotAlways, T.motion.SEAT_F, 0);
  const stOut = 1 - prog(f, sc10.to - 13, sc10.to - 5); // gone by 1128, before the tab glide at 1129 (lesson 42)
  // the short-drop label: on the ghost's first visible frame, out with the ghost (gone ON shortGone)
  const pose = T.cat(f);
  const ghostOn = f >= T.sfx.shortStart && f < T.sfx.shortGone && pose.ghost > 0 && pose.vis > 0;
  const shortOp = ghostOn ? (f < T.sfx.shortTurn ? 1 : Math.min(1, pose.vis / 0.5)) : 0;
  return (
    <>
      <SceneTag x={INSET.x1} y={INSET.y1 + 12} enter={sc07.from} exit={sc07.to} text={T.labels.drawn} anchor="right" />
      {f < sc10.to ? <Stamp x={758} y={420} text={STAMP_TEXT} k={st.k} angle={-9} size={42} opacity={stOut} /> : null}
      {shortOp > 0 ? <Label x={140} y={1004} text={SHORT_LABEL} size={28} variant="probably" opacity={shortOp} /> : null}
    </>
  );
};
