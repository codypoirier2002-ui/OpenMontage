// THE DEVICES below the proton (ROOT: Composition.tsx mounts <RootDevices/> once, above the ladder, under the scenes) and
// the window's drawn atom. All driven by props.devices (build_props.py), pure functions of the frame. Hooks at the top
// (lesson 1). No blend modes (lesson 24).
//   ELECTRON   sc08 ->: a cap under the rail's bottom (L 18) + an OPEN downward dashed arrow (no floor found) + 'ELECTRON'
//              (in from electronIn) + 'no size found · < 10⁻¹⁸ m' SEATING on noSize. The marker does not move.
//   BREAK      sc09 ->: the rail continues past L 18 through a drawn zigzag (y 1012-1040) to the Planck line (draws from breakDraw).
//   PLANCK     sc09 ->: the dashed violet line at y 1080 + 'PLANCK LENGTH · 1.6 × 10⁻³⁵ m' (fully in ON planckIn); it
//              brightens ON floorGlow with 'a floor? unproven' seating there (sc11).
//   READOUT    sc10 ->: '0.' + 34 zeros + '16 m' typed glyph by glyph (readoutStart -> readoutEnd) on a card in the window's column.
//   ATOM       <AtomDrawing/> (the window's 4th state, DRAWN: an electron-cloud haze + a tiny bright nucleus, pulsing ON
//              nucleusPulse) and <AtomNote/> (overlay plane: 'to scale, this dot would be ~0.006 px', seating ON nucleusPulse).
//   <Ping/>    a one-shot ring for the scenes' emphasis.

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { prog, useT } from "../time";
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

const Electron: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const e = T.dev.electron;
  const a = T.ch(e.alpha, frame);
  const s = T.seat(frame, e.subSeat, T.motion.SEAT_F, 14);
  if (a <= 0) return null;
  const E = L.electron;
  const yB = R.y1;
  const ax = R.rungX1 + 8;
  return (
    <>
      <svg width={L.W} height={L.H} style={{ ...FULL, opacity: a }}>
        {/* the cap under L 18 and the open arrow down: nothing found to stand on */}
        <path d={`M ${R.rungX0} ${yB - 8} L ${R.rungX0} ${yB} L ${R.rungX1} ${yB} L ${R.rungX1} ${yB - 8}`} stroke={C.bone} strokeWidth={2.5} fill="none" strokeLinecap="round" />
        <line x1={ax} y1={yB - 30} x2={ax} y2={yB + 44} stroke={C.bone} strokeWidth={2} strokeDasharray="5 6" />
        <path d={`M ${ax - 9} ${yB + 34} L ${ax} ${yB + 48} L ${ax + 9} ${yB + 34}`} stroke={C.bone} strokeWidth={2.5} fill="none" strokeLinecap="round" strokeLinejoin="round" />
        <line x1={ax} y1={E.nameY} x2={E.x - 8} y2={E.nameY} stroke={rgba(C.steel, 0.6)} strokeWidth={1.5} />
      </svg>
      <div style={{ position: "absolute", left: E.x, top: E.nameY - 17, height: 34, fontFamily: FONT.display, fontWeight: 700, fontSize: 32, lineHeight: "34px", color: C.bone,
        opacity: a, whiteSpace: "nowrap", letterSpacing: 1 }}>
        {e.name}
      </div>
      {s.visible ? (
        <div style={{ position: "absolute", left: E.x, top: E.subY - 14 + s.y, height: 30, fontFamily: FONT.mono, fontWeight: 400, fontSize: 28, lineHeight: "30px", color: C.steel,
          opacity: s.opacity * a, whiteSpace: "nowrap" }}>
          <Sci text={e.sub} size={28} />
        </div>
      ) : null}
    </>
  );
};

const Break: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const b = T.ch(T.dev.brk, frame);
  if (b <= 0) return null;
  const x = R.x;
  const y0 = R.y1;
  const d = `M ${x} ${y0} L ${x} ${R.breakY0} L ${x + 12} ${R.breakY0 + 7} L ${x - 12} ${R.breakY0 + 14} L ${x + 12} ${R.breakY0 + 21} L ${x} ${R.breakY1} L ${x} ${R.planckY}`;
  return (
    <svg width={L.W} height={L.H} style={FULL}>
      <path d={d} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - b} stroke={C.steel} strokeWidth={3} fill="none" strokeLinejoin="round" opacity={0.85} />
    </svg>
  );
};

const Planck: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const p = T.dev.planck;
  const a = T.ch(p.alpha, frame);
  const g = T.ch(p.glow, frame);
  const s = T.seat(frame, p.floorSeat, T.motion.SEAT_F, 12);
  if (a <= 0) return null;
  const x0 = R.tickX0 - 40;
  const x1 = 900;
  const xd = x0 + (x1 - x0) * Math.min(1, a * 1.25);
  const [name, val] = p.label.split(" · ");
  return (
    <>
      <svg width={L.W} height={L.H} style={FULL}>
        {g > 0 ? <line x1={x0} y1={p.y} x2={xd} y2={p.y} stroke={C.planck} strokeWidth={10} opacity={0.25 * g} strokeDasharray="14 10" /> : null}
        <line x1={x0} y1={p.y} x2={xd} y2={p.y} stroke={C.planck} strokeWidth={3 + 1 * g} strokeDasharray="14 10" opacity={(0.7 + 0.3 * g) * a} />
      </svg>
      <div style={{ position: "absolute", left: R.labelX + 20, top: p.y + 6, height: 32, fontSize: 28, lineHeight: "32px", color: C.planck, opacity: a, whiteSpace: "nowrap",
        textShadow: g > 0 ? `0 0 14px ${rgba(C.planck, 0.55 * g)}` : "none" }}>
        <span style={{ fontFamily: FONT.display, fontWeight: 700 }}>{name}</span>
        <span style={{ fontFamily: FONT.display, fontWeight: 700 }}> · </span>
        <span style={{ fontFamily: FONT.mono, fontWeight: 500 }}><Sci text={val} size={28} /></span>
      </div>
      {s.visible ? (
        <div style={{ position: "absolute", right: L.W - 900, top: p.y - 40 + s.y, height: 30, fontFamily: FONT.mono, fontWeight: 500, fontSize: 26, lineHeight: "30px", color: C.planck,
          opacity: s.opacity, whiteSpace: "nowrap" }}>
          {p.floor}
        </div>
      ) : null}
    </>
  );
};

const Readout: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const r = T.dev.readout;
  const a = T.ch(r.alpha, frame);
  if (a <= 0) return null;
  const n = r.count[Math.max(0, Math.min(r.count.length - 1, Math.floor(frame)))];
  const b = L.readout;
  let left = n;
  const shown = r.lines.map((l) => {
    const s = l.slice(0, Math.max(0, left));
    left -= l.length;
    return s;
  });
  return (
    <div style={{ position: "absolute", left: b.x0, top: b.y0, width: b.x1 - b.x0, height: b.y1 - b.y0, boxSizing: "border-box", padding: "0 12px", borderRadius: b.r,
      backgroundColor: rgba(C.chip, 0.92), border: `1.5px solid ${rgba(C.steel, 0.5)}`, opacity: a, display: "flex", flexDirection: "column", justifyContent: "center",
      fontFamily: FONT.mono, fontWeight: 500, fontSize: b.px, lineHeight: "40px", color: C.bone, whiteSpace: "pre" }}>
      {shown.map((s, i) => (
        <div key={i} style={{ height: 40 }}>{s}</div>
      ))}
    </div>
  );
};

/** ROOT: the devices on the picture layer (above the ladder, under the scenes, the window and the counter) */
export const RootDevices: React.FC = () => {
  return (
    <>
      <Break />
      <Planck />
      <Electron />
      <Readout />
    </>
  );
};

/** the window's DRAWN atom (inside <WindowFrame/>): an electron-cloud haze + a tiny bright nucleus that pulses ON nucleusPulse */
export const AtomDrawing: React.FC<{ w: number; h: number }> = ({ w, h }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const pulse = T.dev.atomNote.pulse;
  const lf = T.loopFrame(frame);
  const up = prog(frame, pulse - 6, pulse);
  const down = 1 - prog(frame, pulse, pulse + 18);
  const k = frame < pulse ? up : down;
  const cx = w / 2;
  const cy = h * 0.58;
  const breathe = 1 + 0.02 * Math.sin((lf / 50) * Math.PI * 2);
  return (
    <svg width={w} height={h} style={{ position: "absolute", inset: 0 }}>
      <defs>
        <radialGradient id="atomCloud" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={C.steel} stopOpacity={0.42} />
          <stop offset="35%" stopColor={C.steel} stopOpacity={0.24} />
          <stop offset="70%" stopColor={C.steelDim} stopOpacity={0.1} />
          <stop offset="100%" stopColor={C.steelDim} stopOpacity={0} />
        </radialGradient>
      </defs>
      <rect width={w} height={h} fill={C.skyBottom} />
      <circle cx={cx} cy={cy} r={150 * breathe} fill="url(#atomCloud)" />
      {[0.42, 0.7, 0.95].map((q, i) => (
        <circle key={i} cx={cx} cy={cy} r={150 * q * breathe} fill="none" stroke={C.steel} strokeWidth={1} strokeDasharray="2 7" opacity={0.25} />
      ))}
      {k > 0 ? <circle cx={cx} cy={cy} r={6 + 26 * k} fill="none" stroke={C.marker} strokeWidth={2} opacity={0.7 * k} /> : null}
      <circle cx={cx} cy={cy} r={5 + 4 * k} fill={C.marker} opacity={0.35} />
      <circle cx={cx} cy={cy} r={2.5 + 1.5 * k} fill={C.marker} />
    </svg>
  );
};

/** OVERLAY: the note under the drawn atom's title area, inside the window; seats ON nucleusPulse, leaves with the window */
export const AtomNote: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const n = T.dev.atomNote;
  const a = T.ch(n.alpha, frame);
  const s = T.seat(frame, n.seat, T.motion.SEAT_F, 12);
  if (a <= 0 || !s.visible) return null;
  const b = L.win;
  return (
    <div style={{ position: "absolute", left: b.x0, width: b.x1 - b.x0, top: b.y0 + 34 + s.y, display: "flex", flexDirection: "column", alignItems: "center",
      fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "30px", color: C.bone, opacity: a * s.opacity, whiteSpace: "nowrap" }}>
      {n.lines.map((l, i) => (
        <div key={i}><Sci text={l} size={24} /></div>
      ))}
    </div>
  );
};
