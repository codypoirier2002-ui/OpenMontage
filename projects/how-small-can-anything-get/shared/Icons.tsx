// SVG arrows + small icons (lesson 10: no face carries '→'; pattern of projects/how-a-cat-lands/shared/Icons.tsx, video 15).
//   <Arrow x1 y1 x2 y2 .../>        a straight arrow with an open chevron head (svg; e.g. 'falling toward the Sun' on the plate)
//   <CurvedArrow d hx hy ha .../>   an arrow along any SVG path `d` (head at its end) - the orbit inset's direction
//   <ArrowLabel x y text .../>      an HTML label whose '→' is DRAWN (text split on ' -> ' or '→')
//   <WalkerIcon x y size/>          a tiny walking figure (sc01's WALK rung)   <SeatedIcon/> a seated figure (the YOU tag)
// Pure components (no hooks). Draw the svg ones inside your own <svg> (they return SVG elements).

import React from "react";
import { C, FONT } from "../theme";

export const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; color?: string; width?: number; head?: number; opacity?: number; dash?: string }> = ({
  x1, y1, x2, y2, color = C.bone, width = 4, head = 14, opacity = 1, dash,
}) => {
  const a = Math.atan2(y2 - y1, x2 - x1);
  const h1 = [x2 - head * Math.cos(a - 0.5), y2 - head * Math.sin(a - 0.5)];
  const h2 = [x2 - head * Math.cos(a + 0.5), y2 - head * Math.sin(a + 0.5)];
  return (
    <g opacity={opacity} stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" fill="none">
      <path d={`M ${x1} ${y1} L ${x2} ${y2}`} strokeDasharray={dash} />
      <path d={`M ${h1[0]} ${h1[1]} L ${x2} ${y2} L ${h2[0]} ${h2[1]}`} />
    </g>
  );
};

/** an arrow along `d`, its head at (hx, hy) pointing along angle `ha` (radians) */
export const CurvedArrow: React.FC<{ d: string; hx: number; hy: number; ha: number; color?: string; width?: number; head?: number; opacity?: number; dash?: string }> = ({
  d, hx, hy, ha, color = C.bone, width = 4, head = 14, opacity = 1, dash,
}) => (
  <g opacity={opacity} stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" fill="none">
    <path d={d} strokeDasharray={dash} />
    <path d={`M ${hx - head * Math.cos(ha - 0.5)} ${hy - head * Math.sin(ha - 0.5)} L ${hx} ${hy} L ${hx - head * Math.cos(ha + 0.5)} ${hy - head * Math.sin(ha + 0.5)}`} />
  </g>
);

/** HTML: 'before → after' with the arrow DRAWN (write the text with ' -> '); mono 24 px by default */
export const ArrowLabel: React.FC<{ x: number; y: number; text: string; size?: number; color?: string; opacity?: number }> = ({ x, y, text, size = 24, color = C.bone, opacity = 1 }) => {
  const parts = text.split(/\s*(?:->|→)\s*/);
  const ah = size * 0.5;
  return (
    <div style={{ position: "absolute", left: x, top: y, display: "flex", alignItems: "center", gap: size * 0.3, fontFamily: FONT.mono, fontWeight: 400, fontSize: size, color, opacity, whiteSpace: "nowrap" }}>
      {parts.map((p, i) => (
        <React.Fragment key={i}>
          {i > 0 ? (
            <svg width={ah * 1.6} height={ah} viewBox={`0 0 ${ah * 1.6} ${ah}`} style={{ display: "block" }}>
              <Arrow x1={1} y1={ah / 2} x2={ah * 1.6 - 2} y2={ah / 2} color={color} width={Math.max(2, size * 0.09)} head={ah * 0.5} />
            </svg>
          ) : null}
          <span>{p}</span>
        </React.Fragment>
      ))}
    </div>
  );
};

/** a tiny walking figure (svg), centred on (x, y), `size` tall; `phase` 0..1 swings the legs */
export const WalkerIcon: React.FC<{ x: number; y: number; size?: number; color?: string; phase?: number; opacity?: number }> = ({ x, y, size = 26, color = C.steel, phase = 0, opacity = 1 }) => {
  const s = size / 26;
  const sw = Math.max(1.5, 2.2 * s);
  const k = Math.sin(phase * Math.PI * 2) * 5 * s;
  return (
    <g opacity={opacity} stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" fill="none" transform={`translate(${x} ${y - size / 2})`}>
      <circle cx={0} cy={3 * s} r={3 * s} fill={color} stroke="none" />
      <path d={`M 0 ${6 * s} L 0 ${15 * s}`} />
      <path d={`M 0 ${9 * s} L ${-5 * s + k * 0.4} ${13 * s} M 0 ${9 * s} L ${5 * s - k * 0.4} ${12 * s}`} />
      <path d={`M 0 ${15 * s} L ${-4 * s - k} ${24 * s} M 0 ${15 * s} L ${4 * s + k} ${24 * s}`} />
    </g>
  );
};

/** a tiny seated figure (svg): the YOU tag's icon, centred on (x, y) */
export const SeatedIcon: React.FC<{ x: number; y: number; size?: number; color?: string; opacity?: number }> = ({ x, y, size = 22, color = C.bone, opacity = 1 }) => {
  const s = size / 22;
  const sw = Math.max(1.5, 2 * s);
  return (
    <g opacity={opacity} stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" fill="none" transform={`translate(${x} ${y - size / 2})`}>
      <circle cx={-2 * s} cy={3 * s} r={3 * s} fill={color} stroke="none" />
      <path d={`M ${-2 * s} ${6 * s} L ${-2 * s} ${13 * s} L ${5 * s} ${13 * s} L ${5 * s} ${20 * s}`} />
      <path d={`M ${-2 * s} ${9 * s} L ${4 * s} ${10 * s}`} />
      <path d={`M ${-7 * s} ${20 * s} L ${-7 * s} ${11 * s} M ${-7 * s} ${20 * s} L ${9 * s} ${20 * s}`} />
    </g>
  );
};
