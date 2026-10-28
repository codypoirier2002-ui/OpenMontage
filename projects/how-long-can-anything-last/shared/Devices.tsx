// THE DEVICES of the Lifespan Column (ROOT: Composition.tsx mounts <RootDevices/> once, above the ladder, under the scenes; the
// window's two DRAWN insets; the overlay notes). All driven by props.devices (build_props.py), pure functions of the frame.
// Hooks at the top (lesson 1). No blend modes (lesson 24).
//   BREAK      sc09 ->: a drawn zigzag above the PROTON's open arrow (y 432-458), drawing from breakDraw: the rail cannot go on.
//   FOREVER    sc12: the dashed 'forever?' line rising from the break to y 240 (draw from foreverDraw = 'Maybe', MAYBE page), its label
//              seats ON foreverSeat ('forever'). No sound (the closing sentence is SFX-free).
//   READOUT    sc10 ->: '1' + 33 zeros + ' yr' typed glyph by glyph (readoutStart -> readoutEnd) on a card under the window; fades out
//              before the MAYBE glide.
//   SUN        <SunDrawing/> (the window's 4th state, DRAWN): the Sun disc + a much smaller red dwarf (in ON dwarfIn); each lifetime
//              seats ON its rung's seat. 'drawn · not to scale' (WindowTags).
//   TANK       <TankDrawing/> (the window's 5th state, DRAWN): a water detector tank ringed with idle light sensors, nothing
//              flashing; 'no decay seen' seats ON noDecay.
//   <Ping/>    a one-shot ring for the scenes' emphasis.

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { useT } from "../time";

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

const Break: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const b = T.ch(T.dev.brk, frame);
  if (b <= 0) return null;
  const x = R.x;
  const d = `M ${x} ${R.arrowTip - 2} L ${x} ${R.breakY1} L ${x + 12} ${R.breakY1 - 7} L ${x - 12} ${R.breakY1 - 14} L ${x + 12} ${R.breakY1 - 21} L ${x} ${R.breakY0} L ${x} ${R.foreverY0}`;
  return (
    <svg width={L.W} height={L.H} style={FULL}>
      <path d={d} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - b} stroke={C.steel} strokeWidth={3} fill="none" strokeLinejoin="round" opacity={0.85} />
    </svg>
  );
};

const Forever: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const f = T.dev.forever;
  const d = T.ch(f.draw, frame);
  const s = T.seat(frame, f.labelSeat, T.motion.SEAT_F, 12);
  if (d <= 0) return null;
  const y1 = R.foreverY0 - (R.foreverY0 - R.foreverY1) * d;
  const done = d >= 0.999;
  return (
    <>
      <svg width={L.W} height={L.H} style={FULL}>
        <line x1={R.x} y1={R.foreverY0} x2={R.x} y2={y1} stroke={C.bone} strokeWidth={3} strokeDasharray="10 9" opacity={0.85} />
        {d > 0.02 ? (
          <path d={`M ${R.x - 10} ${y1 + 14} L ${R.x} ${y1} L ${R.x + 10} ${y1 + 14}`} stroke={C.bone} strokeWidth={3.5} fill="none" strokeLinecap="round" strokeLinejoin="round" opacity={done ? 0.9 : 0.6} />
        ) : null}
      </svg>
      {s.visible ? (
        <div style={{ position: "absolute", left: L.forever.x, top: L.forever.y + s.y, height: 44, fontFamily: FONT.display, fontWeight: 700, fontSize: 38, lineHeight: "44px", color: C.bone,
          opacity: s.opacity, whiteSpace: "nowrap", letterSpacing: 1 }}>
          {f.label}
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
      <Forever />
      <Readout />
    </>
  );
};

/** the window's DRAWN Sun + red dwarf (inside <WindowFrame/>): two discs (NOT to scale), lifetimes seating on their rungs' seats */
export const SunDrawing: React.FC<{ w: number; h: number }> = ({ w, h }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const s = T.dev.sun;
  const lf = T.loopFrame(frame);
  const da = T.ch(s.dwarfAlpha, frame);
  const ss = T.seat(frame, s.sunSeat, T.motion.SEAT_F, 12);
  const ds = T.seat(frame, s.dwarfSeat, T.motion.SEAT_F, 12);
  const breathe = 1 + 0.02 * Math.sin((lf / 50) * Math.PI * 2);
  const cx = w / 2;
  const txt: React.CSSProperties = { position: "absolute", left: 0, width: w, textAlign: "center", whiteSpace: "nowrap" };
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <svg width={w} height={h} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
            <stop offset="45%" stopColor={C.sun} stopOpacity={0.5} />
            <stop offset="100%" stopColor={C.sun} stopOpacity={0} />
          </radialGradient>
          <radialGradient id="dwarfGlow" cx="50%" cy="50%" r="50%">
            <stop offset="40%" stopColor={C.dwarf} stopOpacity={0.45} />
            <stop offset="100%" stopColor={C.dwarf} stopOpacity={0} />
          </radialGradient>
        </defs>
        <rect width={w} height={h} fill={C.skyBottom} />
        <circle cx={cx} cy={105} r={120 * breathe} fill="url(#sunGlow)" />
        <circle cx={cx} cy={105} r={70} fill={C.sun} />
        <g opacity={da}>
          <circle cx={cx} cy={290} r={46 * breathe} fill="url(#dwarfGlow)" />
          <circle cx={cx} cy={290} r={26} fill={C.dwarf} />
        </g>
      </svg>
      <div style={{ ...txt, top: 186, fontFamily: FONT.mono, fontWeight: 500, fontSize: 26, lineHeight: "30px", color: C.bone }}>Sun</div>
      {ss.visible ? (
        <div style={{ ...txt, top: 218 + ss.y, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "28px", color: C.steel, opacity: ss.opacity }}>{s.lifetimes[0]}</div>
      ) : null}
      <div style={{ ...txt, top: 326, fontFamily: FONT.mono, fontWeight: 500, fontSize: 26, lineHeight: "30px", color: C.bone, opacity: da }}>red dwarf</div>
      {ds.visible ? (
        <div style={{ ...txt, top: 358 + ds.y, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "28px", color: C.steel, opacity: ds.opacity }}>{s.lifetimes[1]}</div>
      ) : null}
    </div>
  );
};

/** the window's DRAWN detector tank: a water tank with a ring of idle light sensors; nothing flashes; 'no decay seen' seats ON noDecay */
export const TankDrawing: React.FC<{ w: number; h: number }> = ({ w, h }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const k = T.dev.tank;
  const s = T.seat(frame, k.noteSeat, T.motion.SEAT_F, 12);
  const lf = T.loopFrame(frame);
  const x0 = 56, x1 = w - 56, y0 = 96, y1 = 322, ry = 22;
  const cols = 8, rows = 6;
  const sensors: React.ReactNode[] = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const x = x0 + 18 + ((x1 - x0 - 36) * c) / (cols - 1);
      const y = y0 + ry + 18 + ((y1 - y0 - 2 * ry - 36) * r) / (rows - 1);
      const tw = 0.5 + 0.12 * Math.sin(lf / 31 + r * 1.7 + c * 0.9);
      sensors.push(<circle key={`${r}-${c}`} cx={x} cy={y} r={6} fill="none" stroke={C.steel} strokeWidth={2} opacity={tw} />);
    }
  }
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <svg width={w} height={h} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <linearGradient id="tankWater" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={C.steel} stopOpacity={0.16} />
            <stop offset="100%" stopColor={C.steel} stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <rect width={w} height={h} fill={C.skyBottom} />
        <path d={`M ${x0} ${y0} L ${x0} ${y1} A ${(x1 - x0) / 2} ${ry} 0 0 0 ${x1} ${y1} L ${x1} ${y0} Z`} fill="url(#tankWater)" stroke={C.steel} strokeWidth={3} />
        <ellipse cx={w / 2} cy={y0} rx={(x1 - x0) / 2} ry={ry} fill={rgba(C.steel, 0.1)} stroke={C.steel} strokeWidth={3} />
        {sensors}
      </svg>
      <div style={{ position: "absolute", left: 0, width: w, top: 30, textAlign: "center", fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "28px", color: C.steel, whiteSpace: "nowrap" }}>
        water detector
      </div>
      {s.visible ? (
        <div style={{ position: "absolute", left: 0, width: w, top: 346 + s.y, textAlign: "center", fontFamily: FONT.mono, fontWeight: 500, fontSize: 26, lineHeight: "30px", color: C.bone,
          opacity: s.opacity, whiteSpace: "nowrap" }}>
          {k.note}
        </div>
      ) : null}
    </div>
  );
};
