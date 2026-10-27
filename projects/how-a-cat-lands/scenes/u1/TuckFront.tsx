// sc06 · TuckFront ★ HERO (U1). 'It tucks its front legs, and the front half spins fast,'
// The pose is the curves' (props.cat): the front legs tuck tuckStart -> tuckSeat; then from turnStart (X5 creak on the
// first moving frame) to turnEnd the FRONT half rolls +200 deg (fast) while the BACK half rolls -20 deg (a little, the other
// way); the dials (<DialsLive/>) read the same curves and 'total spin: 0' never changes. U1 builds the hero look AROUND
// the cat, reading (never re-authoring) the pose, inside the cat's own transform:
//   - TUCK: an amber fold arrow beside the front legs, first visible ON tuckStart, out before the turn.
//   - TURN: a roll ring around each half (a dashed track in the half's colour from turnStart) and an arc on it: the FRONT
//     arc sweeps clockwise as far as the front half has rolled (0 -> 200 deg, the dial's convention: clockwise = +), with
//     amber speed streaks whose strength follows the curve's own speed; the BACK arc sweeps the other way (counter-
//     clockwise), drawn at 2.5x its roll so a 20 deg turn is legible (direction + 'a little'; the dials carry the true
//     relative size, lesson 33: no numbers anywhere).
//   - 'total spin: 0' pulses once (a steel ring around the readout) at the turn's fastest point: still 0.
//   - <ArrowLabel> 'legs in → spins fast' ON turnStart (with the front arc's track), 'legs out → turns slowly' with the
//     back arc's first legible frame; field y 860-990.
// Everything of U1's own is gone by turnEnd (the seam table: finish by 650; the SKATER pulse is 653). The cat keeps
// axes={1} through 650 (U2 mounts axes={1} at 651). Amber only on the front half's marks, cyan only on the back's.
// Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { ArrowLabel, CurvedArrow } from "../../shared/Icons";
import { CatLive, CAT } from "../../shared/Cat";
import { DialsLive } from "../../shared/Dials";
import { measure } from "../../shared/Type";
import { C, E, L, rgba } from "../../theme";
import { prog, useT } from "../../time";

const LABEL_IN = "legs in → spins fast";
const LABEL_OUT = "legs out → turns slowly";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const RING = { cx: 64, rx: 42, ry: 96 }; // each half's roll ring, in the half's own frame (cx along the half)
const BACK_GAIN = 2.5;
const rad = (d: number) => (d * Math.PI) / 180;

/** points of the ring (rx, ry around (cx, 0)) from angle a0 to a1 (deg, 0 = top, + = clockwise on screen) */
const ringPath = (cx: number, rx: number, ry: number, a0: number, a1: number) => {
  const n = Math.max(2, Math.ceil(Math.abs(a1 - a0) / 3));
  let d = "";
  for (let i = 0; i <= n; i++) {
    const a = rad(a0 + ((a1 - a0) * i) / n);
    d += `${i ? " L" : "M"} ${(cx + rx * Math.sin(a)).toFixed(2)} ${(-ry * Math.cos(a)).toFixed(2)}`;
  }
  return d;
};
const ringPt = (cx: number, rx: number, ry: number, a: number) => [cx + rx * Math.sin(rad(a)), -ry * Math.cos(rad(a))];
/** travel direction (radians, svg) at angle a for a sweep of sign s */
const ringTan = (rx: number, ry: number, a: number, s: number) => Math.atan2(ry * Math.sin(rad(a)) * s, rx * Math.cos(rad(a)) * s);

/** a roll arc around one half: dashed track + the arc (sweep deg, signed) + its arrowhead + optional speed streaks */
const RollArc: React.FC<{ dir: -1 | 1; sweep: number; color: string; track: number; op: number; speed: number }> = ({ dir, sweep, color, track, op, speed }) => {
  const cx = dir * RING.cx;
  const s = sweep >= 0 ? 1 : -1;
  const [hx, hy] = ringPt(cx, RING.rx, RING.ry, sweep);
  const ha = ringTan(RING.rx, RING.ry, sweep, s);
  return (
    <g opacity={op}>
      <ellipse cx={cx} cy={0} rx={RING.rx} ry={RING.ry} fill="none" stroke={rgba(color, 0.55 * track)} strokeWidth={3.5} strokeDasharray="7 8" />
      {Math.abs(sweep) > 4 ? (
        <>
          {/* a slate underlay so the arc reads over its own half's tint */}
          <CurvedArrow d={ringPath(cx, RING.rx, RING.ry, 0, sweep)} hx={hx} hy={hy} ha={ha} color={rgba(C.shadow, 0.75)} width={15} head={24} />
          <CurvedArrow d={ringPath(cx, RING.rx, RING.ry, 0, sweep)} hx={hx} hy={hy} ha={ha} color={color} width={9} head={24} />
        </>
      ) : null}
      {speed > 0.05
        ? [0, 1, 2].map((i) => {
            const r = 16 + i * 11;
            const a1 = sweep - s * (8 + i * 6);
            const a0 = a1 - s * (26 + 34 * speed);
            return <path key={i} d={ringPath(cx, RING.rx + r, RING.ry + r, a0, a1)} stroke={rgba(color, 0.7 * speed * (1 - i * 0.25))} strokeWidth={5} strokeLinecap="round" fill="none" />;
          })
        : null}
    </g>
  );
};

export const TuckFront: React.FC<SceneProps> = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const pose = T.cat(frame);
  const prev = T.cat(Math.max(0, frame - 1));
  const sx = T.sfx;
  const fadeOut = 1 - prog(frame, sx.turnEnd - 8, sx.turnEnd, E.calm); // gone ON turnEnd (< 650)
  // TUCK: the fold arrow, first visible ON tuckStart, out by the turn
  const tuck = frame >= sx.tuckStart ? prog(frame, sx.tuckStart - 1, sx.tuckStart + 5) * (1 - prog(frame, sx.turnStart - 10, sx.turnStart - 2, E.calm)) : 0;
  const tuckDraw = prog(frame, sx.tuckStart - 1, sx.tuckSeat, E.calm);
  // TURN: rings + arcs from turnStart
  const turnOn = frame >= sx.turnStart ? fadeOut : 0;
  const track = prog(frame, sx.turnStart - 1, sx.turnStart + 4);
  const fSpeed = Math.min(1, Math.abs(pose.front - prev.front) / 6);
  const bSweep = Math.max(-50, pose.back * BACK_GAIN);
  const backFirst = sx.turnStart + 8; // the back arc's first legible frame (its arrow shows from |sweep| > 4)
  // labels
  const labIn = frame >= sx.turnStart ? prog(frame, sx.turnStart - 1, sx.turnStart + 5) * (1 - prog(frame, sx.turnEnd - 10, sx.turnEnd - 2, E.calm)) : 0;
  const labOut = frame >= backFirst ? prog(frame, backFirst - 1, backFirst + 5) * (1 - prog(frame, sx.turnEnd - 10, sx.turnEnd - 2, E.calm)) : 0;
  // 'total spin: 0' pulse at the turn's fastest point
  const midTurn = Math.round((sx.turnStart + sx.turnEnd) / 2);
  const pk = prog(frame, midTurn - 8, midTurn + 10);
  const pulse = pk > 0 && pk < 1 ? pk : -1;
  const rw = measure(T.labels.total, "monoMed", 28) + 28;
  const rh = 28 * 1.2 + 8;
  const rcx = (L.dials.x0 + L.dials.x1) / 2;
  const rcy = L.dials.readoutY;
  // the cat's own transform (Cat.tsx): translate(x, y + dy) scale(scale); each half rotated by +/- b
  const b = pose.bend / 2 - pose.arch * 7;
  const dy = CAT.legOut * 0.25 * pose.flex;
  const cat = `translate(${pose.x} ${pose.y + dy}) scale(${pose.scale})`;
  return (
    <>
      <CatLive axes={1} />
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        <g transform={cat}>
          {tuck > 0 ? (
            <g transform={`rotate(${b})`} opacity={tuck}>
              {/* from beside the raised forelegs, over and down towards the head: where the paws fold */}
              <path d="M -62 -128 Q -150 -150 -150 -62" pathLength={1} strokeDasharray={`${tuckDraw} 1`} stroke={C.front} strokeWidth={6} strokeLinecap="round" fill="none" />
              {tuckDraw > 0.98 ? <CurvedArrow d="M -150 -64 L -150 -62" hx={-150} hy={-60} ha={Math.PI / 2} color={C.front} width={6} head={16} /> : null}
            </g>
          ) : null}
          {turnOn > 0 ? (
            <>
              <g transform={`rotate(${b})`}>
                <RollArc dir={-1} sweep={pose.front} color={C.front} track={track} op={turnOn} speed={fSpeed} />
              </g>
              <g transform={`rotate(${-b})`}>
                <RollArc dir={1} sweep={bSweep} color={C.back} track={track} op={turnOn} speed={0} />
              </g>
            </>
          ) : null}
        </g>
      </svg>
      <DialsLive />
      {pulse >= 0 ? (
        <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
          <rect x={rcx - rw / 2 - 4 - 16 * pulse} y={rcy - rh / 2 - 4 - 16 * pulse} width={rw + 8 + 32 * pulse} height={rh + 8 + 32 * pulse} rx={12 + 8 * pulse}
            fill="none" stroke={rgba(C.steelLit, 0.9 * Math.sin(pulse * Math.PI))} strokeWidth={4} />
        </svg>
      ) : null}
      {labIn > 0 ? <ArrowLabel x={140} y={890} text={LABEL_IN} size={28} opacity={labIn} /> : null}
      {labOut > 0 ? <ArrowLabel x={140} y={944} text={LABEL_OUT} size={28} opacity={labOut} /> : null}
    </>
  );
};
