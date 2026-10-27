// THE SKATER inset (engine; NEW for video 15; sc07): a small drawn figure skater in steel line, spinning on one skate.
// `arms` 0 = arms out (wide, slow spin lines) -> 1 = arms in (narrow, fast spin lines); `phase` = the spin lines' rotation
// (pass a value that advances faster as arms -> 1, e.g. integrate in your scene from T.sfx.armsIn). Pure svg (inside your
// <svg>), centred on (x, y) = the hips; ~180 px tall at scale 1. One head, two arms, two legs (one lifted).

import React from "react";
import { C, rgba } from "../theme";

export const Skater: React.FC<{ x: number; y: number; arms: number; phase: number; scale?: number; opacity?: number }> = ({ x, y, arms, phase, scale = 1, opacity = 1 }) => {
  const reach = 70 - 52 * arms;
  const lift = 22 - 30 * arms;
  const lines = 3 + Math.round(3 * arms);
  return (
    <g transform={`translate(${x} ${y}) scale(${scale})`} opacity={opacity} stroke={C.steel} strokeLinecap="round" strokeLinejoin="round" fill="none">
      {/* spin lines: ellipse arcs around the body, more and tighter when the arms are in */}
      {Array.from({ length: lines }, (_, i) => {
        const a = phase + (i * 2 * Math.PI) / lines;
        const rx = reach + 30;
        const sx = rx * Math.cos(a), sy = -40 + 14 * Math.sin(a);
        const ex = rx * Math.cos(a + 0.9), ey = -40 + 14 * Math.sin(a + 0.9);
        return <path key={i} d={`M ${sx} ${sy} A ${rx} 14 0 0 1 ${ex} ${ey}`} stroke={rgba(C.steelLit, 0.55)} strokeWidth={3} />;
      })}
      <circle cx={0} cy={-104} r={15} strokeWidth={5} fill={rgba(C.drapeDeep, 0.9)} />
      <path d="M 0 -88 L 0 -12" strokeWidth={7} />
      <path d={`M 0 -74 L ${-reach} ${-74 + lift}`} strokeWidth={6} />
      <path d={`M 0 -74 L ${reach} ${-74 + lift}`} strokeWidth={6} />
      <path d="M 0 -12 L -6 62" strokeWidth={6} />
      <path d="M 0 -12 L 26 26 L 8 40" strokeWidth={6} />
      <path d="M -24 66 L 16 66" strokeWidth={4} stroke={C.steelLit} />
    </g>
  );
};
