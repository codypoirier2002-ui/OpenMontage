// SVG arrows (lesson 10: no face carries '→'; copied from projects/what-if-earth-stopped-spinning/shared/Icons.tsx).
//   <Arrow x1 y1 x2 y2 .../>     a straight arrow with an open chevron head (e.g. U3's converging beam lines)
//   <CurvedArrow d .../>         an arrow along any SVG path `d` (head at its end; pass the end point + direction)
// Pure components (no hooks). Draw inside your own <svg> (they return SVG elements).

import React from "react";
import { C } from "../theme";

export const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; color?: string; width?: number; head?: number; opacity?: number }> = ({
  x1, y1, x2, y2, color = C.bone, width = 5, head = 16, opacity = 1,
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
  d, hx, hy, ha, color = C.bone, width = 5, head = 16, opacity = 1, dash,
}) => (
  <g opacity={opacity} stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" fill="none">
    <path d={d} strokeDasharray={dash} />
    <path d={`M ${hx - head * Math.cos(ha - 0.5)} ${hy - head * Math.sin(ha - 0.5)} L ${hx} ${hy} L ${hx - head * Math.cos(ha + 0.5)} ${hy - head * Math.sin(ha + 0.5)}`} />
  </g>
);
