// THE DEVICES of the Weight Column (ROOT: Composition.tsx mounts <RootDevices/> once, above the ladder, under the scenes; the
// window's drawn black hole; the overlay notes). All driven by props.devices (build_props.py), pure functions of the frame.
// Hooks at the top (lesson 1). No blend modes (lesson 24).
//   BLACK HOLE <BlackHoleDrawing/> (the window's 4th state, DRAWN: a black disc, a thin bright photon ring, a faint glow) and the
//              dashed 'Mercury's orbit' circle drawing around it from orbitDraw (the horizon ~1/5 of the orbit across).
//              <OrbitNote/> (overlay plane): 'Mercury's orbit', seating as the circle closes; leaves with the window.
//   BREAK      sc10 ->: a drawn zigzag above the rail's top (y 345-370), drawing from breakDraw: the rail cannot reach what follows.
//   UNIVERSE   sc10 ->: the dashed OBSERVABLE UNIVERSE line above the SGR A* chip + its label (first visible ON universeIn).
//   BARS       sc10 ->: an honest LINEAR comparison in the window's column: the amber 'ordinary matter' bar (in ON universeIn), the
//              translucent violet DARK MATTER bar rising from darkRise and landing ON darkSeat at 5.4 x its height;
//              '~5 : 1 · inferred' seats ON darkSeat; a 'drawn' tag.
//   <Ping/>    a one-shot ring for the scenes' emphasis.

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { useT } from "../time";
import { Sci } from "./Type";

const R = L.rail;
const FULL: React.CSSProperties = { position: "absolute", inset: 0, overflow: "visible" };

/** a one-shot ring: grows r0 -> r1 over `frames` from `at` (peak ON `at`), fading */
export const Ping: React.FC<{ at: number; x: number; y: number; r0?: number; r1?: number; frames?: number; color?: string; strength?: number }> = ({
  at, x, y, r0 = 8, r1 = 40, frames = 16, color = C.bone, strength = 0.7,
}) => {
  const frame = useCurrentFrame();
  if (frame < at || frame > at + frames) return null;
  const k = (frame - at) / frames;
  const e = 1 - (1 - k) * (1 - k);
  return (
    <svg width={L.W} height={L.H} style={FULL}>
      <circle cx={x} cy={y} r={r0 + (r1 - r0) * e} fill="none" stroke={color} strokeWidth={2.5 * (1 - 0.6 * k)} opacity={strength * (1 - k)} />
    </svg>
  );
};

/** an arc of the circle (cx, cy, r) from 12 o'clock, clockwise, fraction d (a closed circle at d >= 1) */
const arc = (cx: number, cy: number, r: number, d: number) => {
  if (d >= 0.9999) return `M ${cx} ${cy - r} A ${r} ${r} 0 1 1 ${cx} ${cy + r} A ${r} ${r} 0 1 1 ${cx} ${cy - r}`;
  const t = d * 2 * Math.PI;
  return `M ${cx} ${cy - r} A ${r} ${r} 0 ${t > Math.PI ? 1 : 0} 1 ${cx + r * Math.sin(t)} ${cy - r * Math.cos(t)}`;
};

/** the drawn black hole's geometry inside the window (w x h): centre + the orbit's radius */
export const bhGeom = (w: number, h: number) => ({ cx: w / 2, cy: h * 0.56, orbitR: 140 });

const Break: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const b = T.ch(T.dev.brk, frame);
  if (b <= 0) return null;
  const x = R.x;
  const d = `M ${x} ${R.y0} L ${x} ${R.breakY1} L ${x + 12} ${R.breakY1 - 6} L ${x - 12} ${R.breakY1 - 12} L ${x + 12} ${R.breakY1 - 18} L ${x} ${R.breakY0} L ${x} ${R.breakY0 - 18}`;
  return (
    <svg width={L.W} height={L.H} style={FULL}>
      <path d={d} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - b} stroke={C.steel} strokeWidth={3} fill="none" strokeLinejoin="round" opacity={0.85} />
    </svg>
  );
};

const Universe: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const u = T.dev.universe;
  const a = T.ch(u.alpha, frame);
  if (a <= 0) return null;
  const U = L.universe;
  const [name, val] = u.lines[0].split(" · ");
  return (
    <>
      <svg width={L.W} height={L.H} style={{ ...FULL, opacity: a }}>
        <line x1={U.x0} y1={U.y} x2={U.x1} y2={U.y} stroke={C.bone} strokeWidth={3} strokeDasharray="14 10" opacity={0.85} />
      </svg>
      <div style={{ position: "absolute", left: U.labelX, top: U.labelY, opacity: a, color: C.bone, whiteSpace: "nowrap" }}>
        <div style={{ height: 32, lineHeight: "32px", fontSize: 28 }}>
          <span style={{ fontFamily: FONT.display, fontWeight: 700 }}>{name}</span>
          <span style={{ fontFamily: FONT.display, fontWeight: 700, color: C.steel }}> · </span>
          <span style={{ fontFamily: FONT.mono, fontWeight: 500, fontSize: 26 }}><Sci text={val} size={26} /></span>
        </div>
        <div style={{ height: 28, lineHeight: "28px", fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.steel }}>{u.lines[1]}</div>
      </div>
    </>
  );
};

const Bars: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const b = T.dev.bars;
  const oa = T.ch(b.ordAlpha, frame);
  const rise = T.ch(b.rise, frame);
  const s = T.seat(frame, b.seat, T.motion.SEAT_F, 14);
  if (oa <= 0) return null;
  const B = L.bars;
  const darkH = B.ordH * b.ratio * rise;
  return (
    <>
      <svg width={L.W} height={L.H} style={FULL}>
        <line x1={B.x0} y1={B.base} x2={B.x1} y2={B.base} stroke={C.steel} strokeWidth={2} opacity={0.8 * oa} />
        <rect x={B.ordX0} y={B.base - B.ordH} width={B.ordX1 - B.ordX0} height={B.ordH} rx={4} fill={C.amber} opacity={0.92 * oa} />
        {darkH > 0 ? (
          <rect x={B.darkX0} y={B.base - darkH} width={B.darkX1 - B.darkX0} height={darkH} rx={4} fill={rgba(C.dark, 0.38)} stroke={C.dark} strokeWidth={2.5} />
        ) : null}
      </svg>
      <div style={{ position: "absolute", left: B.ordX0 - 16, top: B.base + 10, height: 30, lineHeight: "30px", fontFamily: FONT.mono, fontWeight: 500, fontSize: 24, color: C.bone,
        opacity: oa, whiteSpace: "nowrap" }}>
        {b.ordLabel}
      </div>
      {darkH > 0 ? (
        <div style={{ position: "absolute", right: L.W - B.x1, top: B.base - darkH - 40, height: 34, lineHeight: "34px", fontFamily: FONT.display, fontWeight: 700, fontSize: 30,
          color: C.dark, whiteSpace: "nowrap", letterSpacing: 0.5 }}>
          {b.darkLabel}
        </div>
      ) : null}
      {s.visible ? (
        <div style={{ position: "absolute", left: B.ordX0 - 16, top: B.base - B.ordH * 3.2 + s.y, opacity: s.opacity, display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ fontFamily: FONT.mono, fontWeight: 500, fontSize: 30, lineHeight: "34px", color: C.dark, whiteSpace: "nowrap" }}>
            <Sci text={b.ratioLabel.split(" · ")[0]} size={30} />
          </div>
          <div style={{ fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "28px", color: C.dark, whiteSpace: "nowrap" }}>{b.ratioLabel.split(" · ")[1]}</div>
        </div>
      ) : null}
    </>
  );
};

/** ROOT: the devices on the picture layer (above the ladder, under the scenes, the window and the counter) */
export const RootDevices: React.FC = () => {
  return (
    <>
      <Break />
      <Universe />
      <Bars />
    </>
  );
};

/** OVERLAY: the bars' 'drawn' tag (with the ordinary bar, top left of the column) */
export const BarsTag: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const oa = T.ch(T.dev.bars.ordAlpha, frame);
  if (oa <= 0) return null;
  return (
    <div style={{ position: "absolute", left: L.bars.x0 + 4, top: 404, height: 36, padding: "0 12px", display: "flex", alignItems: "center", backgroundColor: rgba(C.shadow, 0.82),
      borderRadius: 6, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.bone, whiteSpace: "nowrap", opacity: oa }}>
      {T.dev.bars.tag}
    </div>
  );
};

/** the window's DRAWN black hole (inside <WindowFrame/>): a black disc, a thin bright photon ring, a faint glow; the dashed
 *  'Mercury's orbit' circle draws around it from orbitDraw */
export const BlackHoleDrawing: React.FC<{ w: number; h: number }> = ({ w, h }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const o = T.dev.orbit;
  const d = T.ch(o.draw, frame);
  const lf = T.loopFrame(frame);
  const { cx, cy, orbitR } = bhGeom(w, h);
  const rh = orbitR * o.horizon;
  const breathe = 1 + 0.03 * Math.sin((lf / 45) * Math.PI * 2);
  return (
    <svg width={w} height={h} style={{ position: "absolute", inset: 0 }}>
      <defs>
        <radialGradient id="bhGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={C.marker} stopOpacity={0.3} />
          <stop offset="45%" stopColor={C.marker} stopOpacity={0.12} />
          <stop offset="100%" stopColor={C.marker} stopOpacity={0} />
        </radialGradient>
      </defs>
      <rect width={w} height={h} fill={C.skyBottom} />
      <circle cx={cx} cy={cy} r={rh * 3.2 * breathe} fill="url(#bhGlow)" />
      <circle cx={cx} cy={cy} r={rh * 1.12} fill="none" stroke={C.marker} strokeWidth={2.5} opacity={0.95} />
      <circle cx={cx} cy={cy} r={rh * 1.12} fill="none" stroke={C.marker} strokeWidth={7} opacity={0.18} />
      <circle cx={cx} cy={cy} r={rh} fill="#000000" />
      {d > 0 ? <path d={arc(cx, cy, orbitR, d)} fill="none" stroke={C.bone} strokeWidth={2.5} strokeDasharray="9 8" opacity={0.85} /> : null}
    </svg>
  );
};

/** OVERLAY: 'Mercury's orbit' over the drawn circle, inside the window; seats ON labelSeat, leaves with the window */
export const OrbitNote: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const o = T.dev.orbit;
  const open = T.win(frame);
  const s = T.seat(frame, o.labelSeat, T.motion.SEAT_F, 12);
  if (open <= 0 || !s.visible || T.tagAt(frame) !== T.labels.drawn) return null;
  const b = L.win;
  const { cy, orbitR } = bhGeom(b.x1 - b.x0, b.y1 - b.y0);
  return (
    <div style={{ position: "absolute", left: b.x0, width: b.x1 - b.x0, top: b.y0 + cy - orbitR - 46 + s.y, display: "flex", justifyContent: "center",
      fontFamily: FONT.mono, fontWeight: 500, fontSize: 26, lineHeight: "30px", color: C.bone, opacity: open * s.opacity, whiteSpace: "nowrap" }}>
      {o.label}
    </div>
  );
};
