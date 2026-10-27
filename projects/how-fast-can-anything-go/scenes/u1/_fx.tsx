// U1 helpers (sc01-sc06): small emphasis devices drawn AROUND the root ladder (never a second marker, nothing on 'c').
// Every colour is steel / bone (the marker white-cyan and the wall red are root-only). Every trigger is a key frame, a
// root curve or a rung seat read through useT(); hooks at the top of every component before any early return (lesson 1).
//   useDecadePasses(from, to)   the frames inside [from, to) on which the marker's L crosses a decade tick (10, 100, ...)
//   <TickFlashes from to/>      a short bone flash on each decade tick as the marker crosses it (the log scale: each tick is 10x)
//   <Ping at x y .../>          one small ring emitted ON `at` (an arrival / a launch), r0 -> r1 over `frames`, fading
//   <RailGlint/>                sc01: a bone glint riding the draw head while the rail draws bright (railDraw 0 -> 1); it
//                               stops 14 px under 'c' and is gone before the draw reaches the line
//   <BowWave from seat/>        sc04: two faint steel arcs ahead of the marker while it climbs to SOUND (the air it pushes);
//                               gone ON the seat, where the root ring takes over
//   <JumpTrail/>                sc05: the WALK ghost (an outline where the YOU tag sat), a dashed trail with a chevron that
//                               follows the tag up the rail from jumpStart, a launch ring ON jumpStart and a landing flash ON
//                               earthSeat; everything fades 12 f after the seat (gone long before the PROBE page, lesson 42)

import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import { C, L } from "../../theme";
import { prog, useT } from "../../time";
import type { Timing } from "../../time";

const R = L.rail;
const FULL: React.CSSProperties = { position: "absolute", inset: 0 };

/** frames in [from, to) on which the marker's L crosses an integer decade (1..8): { d, f } per decade, in order */
export const decadePasses = (T: Timing, from: number, to: number) => {
  const arr = T.ladderInfo.markerL;
  const out: { d: number; f: number }[] = [];
  const hi = Math.min(to, arr.length);
  for (let d = 1; d <= 8; d++) {
    for (let f = Math.max(1, from); f < hi; f++) {
      if (arr[f - 1] < d && arr[f] >= d) {
        out.push({ d, f });
        break;
      }
    }
  }
  return out;
};

export const useDecadePasses = (from: number, to: number) => {
  const T = useT();
  const passes = useMemo(() => decadePasses(T, from, to), [T, from, to]);
  return passes;
};

/** a bone flash on each decade tick the marker crosses inside [from, to), decaying over `frames` */
export const TickFlashes: React.FC<{ from: number; to: number; frames?: number }> = ({ from, to, frames = 14 }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const passes = useDecadePasses(from, to);
  const live = passes.filter((p) => frame >= p.f && frame < p.f + frames);
  if (live.length === 0) return null;
  return (
    <svg width={L.W} height={L.H} style={FULL}>
      {live.map((p) => {
        const k = (frame - p.f) / frames;
        const y = T.railY(p.d);
        const spread = 4 + 22 * k;
        return (
          <g key={p.d} strokeLinecap="round">
            <line x1={R.tickX0 - spread} y1={y} x2={R.tickX1 + spread} y2={y} stroke={C.steel} strokeWidth={6} opacity={0.3 * (1 - k)} />
            <line x1={R.tickX0 - 4} y1={y} x2={R.tickX1 + 4} y2={y} stroke={C.bone} strokeWidth={2.5} opacity={0.95 * (1 - k)} />
          </g>
        );
      })}
    </svg>
  );
};

/** one ring emitted ON `at` from (x, y): r0 -> r1 over `frames`, fading (an arrival ping / a launch burst) */
export const Ping: React.FC<{ at: number; x: number; y: number; r0?: number; r1?: number; frames?: number; width?: number; color?: string; strength?: number }> = ({
  at, x, y, r0 = 9, r1 = 34, frames = 12, width = 2.5, color = C.steel, strength = 0.9,
}) => {
  const frame = useCurrentFrame();
  const k = prog(frame, at, at + frames);
  if (frame < at || k >= 1) return null;
  const e = 1 - (1 - k) * (1 - k);
  return (
    <svg width={L.W} height={L.H} style={FULL}>
      <circle cx={x} cy={y} r={r0 + (r1 - r0) * e} fill="none" stroke={color} strokeWidth={width * (1 - 0.6 * k)} opacity={strength * (1 - k)} />
    </svg>
  );
};

/** sc01: a glint riding the bright rail's draw head (railDraw 0 -> 1); never reaches 'c' */
export const RailGlint: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const ld = T.ladder(frame);
  const d = ld.railDraw;
  if (d <= 0 || d >= 1) return null;
  const yRaw = R.axisY0 - (R.axisY0 - R.cY) * d;
  const y = Math.max(T.cY + 14, yRaw);
  const a = Math.min(1, (1 - d) / 0.1) * Math.min(1, d / 0.04);
  if (a <= 0) return null;
  return (
    <svg width={L.W} height={L.H} style={FULL}>
      <line x1={R.x} y1={y + 2} x2={R.x} y2={Math.min(R.axisY0, y + 70)} stroke={C.bone} strokeWidth={5} strokeLinecap="round" opacity={0.22 * a} />
      <circle cx={R.x} cy={y} r={11} fill={C.steel} opacity={0.22 * a} />
      <circle cx={R.x} cy={y} r={4.5} fill={C.bone} opacity={0.95 * a} />
    </svg>
  );
};

/** sc04: two faint arcs ahead of the marker while it climbs (from -> seat); gone ON the seat */
export const BowWave: React.FC<{ from: number; seat: number }> = ({ from, seat }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= seat) return null;
  const ld = T.ladder(frame);
  const a = Math.min(1, ld.streak * 3) * (1 - prog(frame, seat - 5, seat));
  if (a <= 0.01) return null;
  const arc = (r: number) => {
    const a0 = Math.PI * 1.15;
    const a1 = Math.PI * 1.85;
    const x0 = R.x + r * Math.cos(a0);
    const y0 = ld.y - 4 + r * Math.sin(a0);
    const x1 = R.x + r * Math.cos(a1);
    const y1 = ld.y - 4 + r * Math.sin(a1);
    return `M ${x0} ${y0} A ${r} ${r} 0 0 1 ${x1} ${y1}`;
  };
  return (
    <svg width={L.W} height={L.H} style={FULL}>
      <path d={arc(15)} stroke={C.steel} strokeWidth={2.5} fill="none" strokeLinecap="round" opacity={0.85 * a} />
      <path d={arc(24)} stroke={C.steel} strokeWidth={1.5} fill="none" strokeLinecap="round" opacity={0.45 * a} />
    </svg>
  );
};

/** sc05: the jump's emphasis around the root YOU tag (never a second tag: no text) */
export const JumpTrail: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const start = T.sfx.jumpStart;
  const seat = T.sfx.earthSeat;
  const hold = 12;
  const fadeF = 12;
  const endF = seat + hold + fadeF;
  if (frame < start || frame >= endF) return null;
  const you = T.you(frame);
  const w = 104;
  const h = L.you.h;
  const left = L.you.right - w;
  const cx = left + w / 2;
  const yWalk = T.railY(T.rung("walk").L);
  const out = 1 - prog(frame, seat + hold, endF);
  const ghostIn = prog(frame, start, start + 6);
  const trailX = left - 10;
  const trailTop = you.y + h / 2 + 4;
  const trailBot = yWalk - h / 2 - 4;
  const trailLen = Math.max(0, trailBot - trailTop);
  const landK = prog(frame, seat, seat + 10);
  const landing = frame >= seat && landK < 1;
  const infl = 2 + 12 * (1 - (1 - landK) * (1 - landK));
  return (
    <svg width={L.W} height={L.H} style={{ ...FULL, opacity: out }}>
      {/* the WALK ghost: the empty chip where the tag sat (it covers the '10' decade number as the tag did) */}
      <rect x={left} y={yWalk - h / 2} width={w} height={h} rx={8} fill={C.chip} fillOpacity={0.88} stroke={C.steel} strokeWidth={1.5} strokeDasharray="5 4" opacity={ghostIn} />
      {/* the trail: a dashed line beside the tag's path, a chevron at its moving end */}
      {trailLen > 24 ? (
        <g stroke={C.steel} strokeWidth={2} fill="none" strokeLinecap="round" strokeLinejoin="round" opacity={0.8}>
          <path d={`M ${trailX} ${trailBot} L ${trailX} ${trailTop + 10}`} strokeDasharray="4 7" />
          <path d={`M ${trailX - 7} ${trailTop + 9} L ${trailX} ${trailTop} L ${trailX + 7} ${trailTop + 9}`} />
        </g>
      ) : null}
      {/* the landing flash: the tag's box inflating once ON the EARTH seat */}
      {landing ? (
        <rect x={left - infl} y={you.y - h / 2 - infl} width={w + 2 * infl} height={h + 2 * infl} rx={8 + infl} fill="none" stroke={C.bone} strokeWidth={2} opacity={0.9 * (1 - landK)} />
      ) : null}
      {/* the launch burst ON jumpStart (the X1 whoosh's first moving frame) */}
      {frame < start + 12 ? (
        <circle cx={cx} cy={yWalk} r={14 + 30 * (1 - (1 - (frame - start) / 12) ** 2)} fill="none" stroke={C.steel} strokeWidth={2} opacity={0.8 * (1 - (frame - start) / 12)} />
      ) : null}
    </svg>
  );
};
