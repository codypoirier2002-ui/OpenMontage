// THE DEVICES (ENGINE for the units; every state is a root curve read through useT(), so a device mounted in two scenes of
// the same unit, or across the sc06 -> sc07 seam, is identical by construction):
//   <YouTagLive/>        the 'YOU' chip + seated figure LEFT of the rail at T.you(f): seats at WALK ON youSeat (gravity drop),
//                        JUMPS with the marker to EARTH (jumpStart -> earthSeat), then sits there to the end. sc05 -> sc12.
//   <PressureRing from/> a single soft ring expanding from the marker from `from` (sc04: the SOUND seat, X2), 24 f.
//   <OrbitInset/>        the drawn orbit diagram (Sun dot, Earth dot on a dashed circle, a direction arrow) in the window's
//                        column, alpha = T.orbit(f) (in from 'riding', GONE before the PROBE page); carries its own
//                        'drawn · not to scale' (>= 24 px). sc05.
//   <LightBeamLive/>     the light beam racing the rail (T.beam(f): progress 0..1, alpha), white-cyan; reaches 'c' ON lightSeat. sc08 -> sc09.
//   <MassLabelLive/>     'anything with mass' at a fixed chip (x 280, y 500) with a dotted leader to the marker; alpha = T.mass(f)
//                        (in on 'nothing', GONE before the LHC page). sc09 -> sc10.
//   <EnergyLive/>        'ENERGY NEEDED': the bar (x 600-650) growing from the rail's foot by T.energy(f).barH (off the top ON
//                        'end') + the small drawn gamma curve with axis labels 'speed' / 'energy' and a dot at v/c; alpha =
//                        T.energy(f).alpha (GONE before the LHC page); 'drawn · not to scale'. sc10.
//   <NinesReadoutLive/>  the readout card ('LHC protons' + '99.9999991 %' typed one glyph per X3 tick, T.nines(f)); seats ON
//                        readoutSeat; constant through the settle. sc11 -> sc12.
// Hooks at the top of every component, before any early return (lesson 1). No blend modes (lesson 24). Marker white-cyan
// ONLY on the beam; nothing here is red.

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, E, FONT, L, rgba } from "../theme";
import { prog, useT } from "../time";
import { CurvedArrow, SeatedIcon } from "./Icons";

const R = L.rail;

export const YouTagLive: React.FC<{ opacity?: number }> = ({ opacity = 1 }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const you = T.you(frame);
  if (you.alpha <= 0) return null;
  const s = T.seat(frame, T.sfx.youSeat, T.motion.SEAT_F, 18);
  const y = you.y + (frame < T.sfx.youSeat ? s.y : 0);
  const w = 104;
  const h = L.you.h;
  return (
    <div style={{ position: "absolute", left: L.you.right - w, top: y - h / 2, width: w, height: h, opacity: you.alpha * s.opacity * opacity }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 8, backgroundColor: rgba(C.chip, 0.92), border: `1.5px solid ${rgba(C.bone, 0.8)}`, boxSizing: "border-box",
        display: "flex", alignItems: "center", gap: 6, padding: "0 8px 0 6px" }}>
        <svg width={24} height={24} viewBox="0 0 24 24"><SeatedIcon x={12} y={12} size={22} /></svg>
        <span style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 26, lineHeight: "30px", color: C.bone, letterSpacing: 1 }}>{T.labels.you}</span>
      </div>
      {/* the stem to the rail */}
      <div style={{ position: "absolute", left: w, top: h / 2 - 1, width: R.rungX0 - L.you.right - 2, height: 2, backgroundColor: rgba(C.bone, 0.7) }} />
    </div>
  );
};

/** one soft pressure ring from the marker, expanding over `frames` from `from` (sc04) */
export const PressureRing: React.FC<{ from: number; frames?: number; maxR?: number }> = ({ from, frames = 24, maxR = 120 }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const k = prog(frame, from, from + frames);
  if (frame < from || k >= 1) return null;
  const ld = T.ladder(from);
  const r = 8 + (maxR - 8) * (1 - (1 - k) ** 2);
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
      <circle cx={R.x} cy={ld.y} r={r} fill="none" stroke={C.steel} strokeWidth={3 * (1 - k) + 1} opacity={0.85 * (1 - k)} />
      <circle cx={R.x} cy={ld.y} r={r * 0.6} fill="none" stroke={C.steel} strokeWidth={1.5} opacity={0.4 * (1 - k)} />
    </svg>
  );
};

export const OrbitInset: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const a = T.orbit(frame);
  if (a <= 0) return null;
  const b = L.orbit;
  const cx = (b.x0 + b.x1) / 2;
  const cy = (b.y0 + b.y1) / 2 - 10;
  const rr = 108;
  const t = (frame - T.sfx.orbitIn) / 110;
  const ang = -Math.PI / 2 - t * Math.PI * 2 * 0.45;
  const ex = cx + rr * Math.cos(ang);
  const ey = cy + rr * Math.sin(ang);
  const a0 = -Math.PI / 2 + 0.35;
  const a1 = -Math.PI / 2 - 0.9;
  const arc = `M ${cx + (rr + 28) * Math.cos(a0)} ${cy + (rr + 28) * Math.sin(a0)} A ${rr + 28} ${rr + 28} 0 0 0 ${cx + (rr + 28) * Math.cos(a1)} ${cy + (rr + 28) * Math.sin(a1)}`;
  return (
    <div style={{ position: "absolute", left: b.x0, top: b.y0, width: b.x1 - b.x0, height: b.y1 - b.y0, opacity: a }}>
      <svg width={b.x1 - b.x0} height={b.y1 - b.y0} viewBox={`${b.x0} ${b.y0} ${b.x1 - b.x0} ${b.y1 - b.y0}`} style={{ position: "absolute", inset: 0 }}>
        <circle cx={cx} cy={cy} r={rr} fill="none" stroke={C.steel} strokeWidth={2} strokeDasharray="8 7" opacity={0.8} />
        <circle cx={cx} cy={cy} r={16} fill={C.bone} opacity={0.95} />
        <circle cx={cx} cy={cy} r={26} fill={C.bone} opacity={0.12} />
        <circle cx={ex} cy={ey} r={7} fill={C.steel} />
        <CurvedArrow d={arc} hx={cx + (rr + 28) * Math.cos(a1)} hy={cy + (rr + 28) * Math.sin(a1)} ha={a1 - Math.PI / 2} color={C.steel} width={3} head={12} />
      </svg>
      <div style={{ position: "absolute", left: 0, bottom: 0, height: 34, padding: "0 10px", display: "flex", alignItems: "center", borderRadius: 6, backgroundColor: rgba(C.shadow, 0.82),
        fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.bone, whiteSpace: "nowrap" }}>
        {T.labels.drawn}
      </div>
    </div>
  );
};

export const LightBeamLive: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const bm = T.beam(frame);
  if (bm.alpha <= 0 || bm.progress <= 0) return null;
  const headR = 7;
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, opacity: bm.alpha }}>
      <line x1={R.x} y1={R.axisY0} x2={R.x} y2={bm.y} stroke={C.marker} strokeWidth={10} strokeLinecap="round" opacity={0.18} />
      <line x1={R.x} y1={R.axisY0} x2={R.x} y2={bm.y} stroke={C.marker} strokeWidth={3} strokeLinecap="round" opacity={0.9} />
      <circle cx={R.x} cy={bm.y} r={headR * 2.6} fill={C.marker} opacity={0.2} />
      <circle cx={R.x} cy={bm.y} r={headR} fill="#FFFFFF" opacity={0.95} />
    </svg>
  );
};

export const MassLabelLive: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const a = T.mass(frame);
  if (a <= 0) return null;
  const ld = T.ladder(frame);
  const x = L.massLabel.x;
  const y = 500;
  return (
    <>
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, opacity: a }}>
        <path d={`M ${x - 4} ${y} L ${R.x + 10} ${ld.y}`} stroke={rgba(C.steel, 0.7)} strokeWidth={1.5} strokeDasharray="3 5" fill="none" />
      </svg>
      <div style={{ position: "absolute", left: x, top: y - 17, height: 34, padding: "0 10px", display: "flex", alignItems: "center", borderRadius: 6, backgroundColor: rgba(C.shadow, 0.82),
        fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.bone, whiteSpace: "nowrap", opacity: a }}>
        {T.labels.mass}
      </div>
    </>
  );
};

export const EnergyLive: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const en = T.energy(frame);
  if (en.alpha <= 0) return null;
  const g = L.energy;
  const cv = g.curve;
  const w = cv.x1 - cv.x0;
  const h = cv.y1 - cv.y0;
  // the drawn curve: gamma(v) = 1 / sqrt(1 - v^2), 0 <= v < 0.995, plotted in a 'speed' x 'energy' box (not to scale)
  const pts: string[] = [];
  for (let i = 0; i <= 60; i++) {
    const v = (i / 60) * 0.992;
    const gm = 1 / Math.sqrt(1 - v * v);
    const yy = cv.y1 - Math.min(1, (gm - 1) / 11) * (h - 24);
    pts.push(`${i === 0 ? "M" : "L"} ${cv.x0 + 24 + v * (w - 36)} ${yy}`);
  }
  const vdot = Math.min(0.992, en.vc);
  const gdot = 1 / Math.sqrt(1 - vdot * vdot);
  const dx = cv.x0 + 24 + vdot * (w - 36);
  const dy = cv.y1 - Math.min(1, (gdot - 1) / 11) * (h - 24);
  const barTop = g.y0 - en.barH;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: en.alpha }}>
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
        {/* the bar (clipped to the frame; it runs off the top) */}
        <rect x={g.barX0} y={Math.max(-20, barTop)} width={g.barX1 - g.barX0} height={Math.max(0, g.y0 - Math.max(-20, barTop))} fill={rgba(C.steel, 0.22)} stroke={C.steel} strokeWidth={2} />
        {en.barH > 2 ? <rect x={g.barX0 + 3} y={Math.max(-20, barTop) + 3} width={g.barX1 - g.barX0 - 6} height={Math.max(0, g.y0 - Math.max(-20, barTop) - 6)} fill={rgba(C.bone, 0.18)} /> : null}
        <line x1={g.barX0 - 10} y1={g.y0} x2={g.barX1 + 10} y2={g.y0} stroke={C.steel} strokeWidth={2} />
        {/* the curve inset */}
        <rect x={cv.x0} y={cv.y0} width={w} height={h} rx={10} fill={rgba(C.chip, 0.85)} stroke={rgba(C.steel, 0.35)} strokeWidth={1} />
        <line x1={cv.x0 + 24} y1={cv.y1 - 24} x2={cv.x1 - 12} y2={cv.y1 - 24} stroke={C.steel} strokeWidth={1.5} opacity={0.8} />
        <line x1={cv.x0 + 24} y1={cv.y1 - 24} x2={cv.x0 + 24} y2={cv.y0 + 12} stroke={C.steel} strokeWidth={1.5} opacity={0.8} />
        <path d={pts.join(" ")} stroke={C.bone} strokeWidth={2.5} fill="none" />
        <circle cx={dx} cy={dy} r={6} fill={C.bone} />
      </svg>
      <div style={{ position: "absolute", left: g.barX0 - 10, top: g.y0 + 8, fontFamily: FONT.display, fontWeight: 700, fontSize: 26, lineHeight: "30px", color: C.bone, whiteSpace: "nowrap", letterSpacing: 0.5 }}>
        {T.energyInfo.label}
      </div>
      <div style={{ position: "absolute", left: cv.x0 + 24 + (w - 36) / 2 - 36, top: cv.y1 - 22, width: 72, textAlign: "center", fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "24px", color: C.steel }}>
        {T.energyInfo.axisX}
      </div>
      <div style={{ position: "absolute", left: cv.x0 + 32, top: cv.y0 + 8, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, lineHeight: "24px", color: C.steel }}>
        {T.energyInfo.axisY}
      </div>
      <div style={{ position: "absolute", left: cv.x0, top: cv.y1 + 6, height: 34, padding: "0 10px", display: "flex", alignItems: "center", borderRadius: 6, backgroundColor: rgba(C.shadow, 0.82),
        fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.bone, whiteSpace: "nowrap" }}>
        {T.energyInfo.tag}
      </div>
    </div>
  );
};

export const NinesReadoutLive: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const nn = T.nines(frame);
  if (nn.alpha <= 0) return null;
  const s = T.seat(frame, T.ninesInfo.seat, T.motion.SEAT_F, 18);
  const b = L.readout;
  const full = T.ninesInfo.value;
  const rest = full.slice(nn.shown.length);
  return (
    <div style={{ position: "absolute", left: b.x0, top: b.y0 + (frame < T.ninesInfo.seat ? s.y : 0), width: b.x1 - b.x0, height: b.y1 - b.y0, borderRadius: b.r, boxSizing: "border-box",
      backgroundColor: rgba(C.chip, 0.92), border: `1.5px solid ${rgba(C.steel, 0.5)}`, padding: "16px 22px", opacity: nn.alpha * s.opacity, boxShadow: "0 14px 40px rgba(0,0,0,0.5)" }}>
      <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 28, lineHeight: "34px", color: C.steel, letterSpacing: 0.5 }}>{T.ninesInfo.label}</div>
      <div style={{ marginTop: 10, fontFamily: FONT.mono, fontWeight: 500, fontSize: 38, lineHeight: "50px", color: C.bone, whiteSpace: "nowrap", fontVariantNumeric: "tabular-nums" }}>
        <span>{nn.shown}</span>
        <span style={{ opacity: 0.16 }}>{rest}</span>
      </div>
    </div>
  );
};

/** the easing the units should use for their own eased moves (re-exported for convenience) */
export const EASE = E;
