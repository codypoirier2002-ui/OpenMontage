// SVG marks (lesson 10: no face carries '→' or '✓'; pattern of projects/how-hot-can-it-get/shared/Icons.tsx).
//   <Arrow x1 y1 x2 y2 .../>        a straight arrow with an open chevron head (e.g. sc04's UP arrow)
//   <CurvedArrow d hx hy ha .../>   an arrow along any SVG path `d` (head at its end)
//   <CheckMark x y size progress/>  the checklist's hand-drawn tick: a two-stroke check that DRAWS with `progress` 0..1
//                                    (the stroke reaches its end exactly at progress 1 = the tick frame)
//   <InnerEarIcon x y size glow/>   the inner ear (sc04): three semicircular canals
//   <ArrowLabel x y text/>          an HTML label whose '→' is drawn as SVG ('legs in → spins fast' ...)
// Pure components (no hooks). Draw inside your own <svg> (they return SVG elements) - except <ArrowLabel> (HTML).

import React from "react";
import { C, FONT, rgba } from "../theme";

export const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; color?: string; width?: number; head?: number; opacity?: number }> = ({
  x1, y1, x2, y2, color = C.shadow, width = 4, head = 14, opacity = 1,
}) => {
  const a = Math.atan2(y2 - y1, x2 - x1);
  const h1 = [x2 - head * Math.cos(a - 0.5), y2 - head * Math.sin(a - 0.5)];
  const h2 = [x2 - head * Math.cos(a + 0.5), y2 - head * Math.sin(a + 0.5)];
  return (
    <g opacity={opacity} stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" fill="none">
      <path d={`M ${x1} ${y1} L ${x2} ${y2}`} />
      <path d={`M ${h1[0]} ${h1[1]} L ${x2} ${y2} L ${h2[0]} ${h2[1]}`} />
    </g>
  );
};

/** an arrow along `d`, its head at (hx, hy) pointing along angle `ha` (radians) */
export const CurvedArrow: React.FC<{ d: string; hx: number; hy: number; ha: number; color?: string; width?: number; head?: number; opacity?: number; dash?: string }> = ({
  d, hx, hy, ha, color = C.shadow, width = 4, head = 14, opacity = 1, dash,
}) => (
  <g opacity={opacity} stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" fill="none">
    <path d={d} strokeDasharray={dash} />
    <path d={`M ${hx - head * Math.cos(ha - 0.5)} ${hy - head * Math.sin(ha - 0.5)} L ${hx} ${hy} L ${hx - head * Math.cos(ha + 0.5)} ${hy - head * Math.sin(ha + 0.5)}`} />
  </g>
);

/** the check mark: short stroke down-right, long stroke up-right; `progress` 0..1 draws it (pathLength-normalised) */
export const CheckMark: React.FC<{ x: number; y: number; size: number; progress: number; color?: string; width?: number }> = ({
  x, y, size, progress, color = C.tickInk, width,
}) => {
  if (progress <= 0) return null;
  const s = size;
  const d = `M ${x + s * 0.12} ${y + s * 0.52} L ${x + s * 0.4} ${y + s * 0.8} L ${x + s * 0.9} ${y + s * 0.14}`;
  return (
    <path d={d} pathLength={1} strokeDasharray={`${Math.min(1, progress)} 1`} stroke={color} strokeWidth={width ?? Math.max(3, s * 0.16)}
      strokeLinecap="round" strokeLinejoin="round" fill="none" />
  );
};

/** the inner ear: a drawn vestibular icon (three semicircular canals on a small vestibule), centred on (x, y); `glow` 0..1 */
export const InnerEarIcon: React.FC<{ x: number; y: number; size: number; color?: string; glow?: number; opacity?: number }> = ({
  x, y, size, color = C.steelLit, glow = 0, opacity = 1,
}) => {
  const s = size / 100;
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} opacity={opacity} fill="none" strokeLinecap="round">
      {glow > 0 ? <circle cx={0} cy={0} r={62} fill={`rgba(244,239,230,${0.18 * glow})`} stroke="none" /> : null}
      <ellipse cx={-6} cy={-22} rx={26} ry={30} stroke={color} strokeWidth={7} />
      <ellipse cx={20} cy={-4} rx={30} ry={18} stroke={color} strokeWidth={7} transform="rotate(-20 20 -4)" />
      <ellipse cx={-22} cy={4} rx={16} ry={28} stroke={color} strokeWidth={7} transform="rotate(30 -22 4)" />
      <ellipse cx={0} cy={24} rx={20} ry={14} fill={color} stroke="none" />
      <path d="M 14 30 C 34 40, 40 58, 30 70" stroke={color} strokeWidth={7} />
    </g>
  );
};

/** a verified string that contains '→' (e.g. 'legs in → spins fast'), set in HTML with the arrow DRAWN as SVG (lesson 10: no
 *  face carries '→'). Absolute at (x, y) = left / vertical centre. Pass the whole verified string (literal scan). */
export const ArrowLabel: React.FC<{ x: number; y: number; text: string; size?: number; color?: string; arrowColor?: string; opacity?: number; chip?: boolean }> = ({
  x, y, text, size = 28, color = C.bone, arrowColor, opacity = 1, chip = true,
}) => {
  const parts = text.split("→").map((p) => p.trim());
  const aw = size * 1.4;
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: "translateY(-50%)", display: "flex", alignItems: "center", gap: size * 0.3, opacity,
      fontFamily: FONT.mono, fontWeight: 500, fontSize: size, color, whiteSpace: "nowrap", padding: chip ? "4px 12px" : 0, borderRadius: 8,
      backgroundColor: chip ? rgba(C.shadow, 0.82) : undefined }}>
      {parts.map((p, i) => (
        <React.Fragment key={i}>
          {i > 0 ? (
            <svg width={aw} height={size} style={{ overflow: "visible" }}>
              <Arrow x1={2} y1={size / 2} x2={aw - 3} y2={size / 2} color={arrowColor ?? color} width={size * 0.12} head={size * 0.38} />
            </svg>
          ) : null}
          <span>{p}</span>
        </React.Fragment>
      ))}
    </div>
  );
};
