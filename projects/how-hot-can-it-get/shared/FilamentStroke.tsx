// Filament strokes: a line that draws itself like a heating tungsten filament - a white-hot core over a wide soft halo in
// the black-body colour of `kelvin` (shared/blackbody.ts), revealed along the path (pathLength 1, dash offset = 1 - q).
//   <Filament d q kelvin width .../>   any SVG path (inside your own <svg>); q = draw progress 0..1
//   <FilamentQ x y h q kelvin opacity/> the film's '?' (ROOT: shared/Ladder.tsx draws it at L.q, 1,800 K; sc02 -> sc12)
// The halo is an SVG feGaussianBlur on its own copy of the path (a filter, not a blend mode: lesson 24). useId() is called
// unconditionally at the top (lesson 1).

import React, { useId } from "react";
import { bbRgb, lighten } from "./blackbody";
import { cssId } from "./noise";

const rgb = (c: [number, number, number], a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

export const Filament: React.FC<{ d: string; q: number; kelvin: number; width?: number; opacity?: number; halo?: number }> = ({
  d, q, kelvin, width = 7, opacity = 1, halo = 1,
}) => {
  const id = cssId(useId(), "fl");
  const c = bbRgb(kelvin);
  const core = lighten(c, 0.55);
  const off = 1 - Math.max(0, Math.min(1, q));
  if (q <= 0 || opacity <= 0) return null;
  return (
    <g opacity={opacity}>
      <defs>
        <filter id={id} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation={width * 1.6} />
        </filter>
      </defs>
      <path d={d} pathLength={1} strokeDasharray="1 1" strokeDashoffset={off} stroke={rgb(c, 0.85 * halo)} strokeWidth={width * 3.2}
        strokeLinecap="round" strokeLinejoin="round" fill="none" filter={`url(#${id})`} />
      <path d={d} pathLength={1} strokeDasharray="1 1" strokeDashoffset={off} stroke={rgb(c)} strokeWidth={width} strokeLinecap="round"
        strokeLinejoin="round" fill="none" />
      <path d={d} pathLength={1} strokeDasharray="1 1" strokeDashoffset={off} stroke={rgb(core)} strokeWidth={width * 0.42} strokeLinecap="round"
        strokeLinejoin="round" fill="none" />
    </g>
  );
};

/** the '?' in a 100 x 160 design box: the hook + stem, then the dot (drawn in the last 10 % of q) */
const Q_PATH = "M 20 48 C 20 14, 80 8, 81 44 C 82 72, 50 74, 50 104 L 50 116";

export const FilamentQ: React.FC<{ x: number; y: number; h: number; q: number; kelvin: number; opacity?: number }> = ({ x, y, h, q, kelvin, opacity = 1 }) => {
  const s = h / 160;
  const stroke = Math.min(1, q / 0.9);
  const dot = Math.max(0, Math.min(1, (q - 0.9) / 0.1));
  return (
    <svg width={100 * s + 80} height={h + 80} style={{ position: "absolute", left: x - 50 * s - 40, top: y - h / 2 - 40, overflow: "visible" }}>
      <g transform={`translate(40 40) scale(${s})`}>
        <Filament d={Q_PATH} q={stroke} kelvin={kelvin} width={9} opacity={opacity} />
        <Filament d="M 50 142 L 50 143.5" q={dot} kelvin={kelvin} width={15} opacity={opacity} />
      </g>
    </svg>
  );
};

/** the '?' UNLIT: a plain iron-grey stroke of the same path (no colour, no halo) - it waits at the top before the ignition */
export const QOutline: React.FC<{ x: number; y: number; h: number; opacity: number }> = ({ x, y, h, opacity }) => {
  const s = h / 160;
  if (opacity <= 0) return null;
  return (
    <svg width={100 * s + 80} height={h + 80} style={{ position: "absolute", left: x - 50 * s - 40, top: y - h / 2 - 40, overflow: "visible", opacity }}>
      <g transform={`translate(40 40) scale(${s})`} stroke="#6B5A4E" fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path d={Q_PATH} strokeWidth={7} />
        <path d="M 50 142 L 50 143.5" strokeWidth={12} />
      </g>
    </svg>
  );
};
