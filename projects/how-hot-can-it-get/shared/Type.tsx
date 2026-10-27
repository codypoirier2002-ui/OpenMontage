// Type helpers (pattern of projects/what-if-earth-stopped-spinning/shared/Type.tsx, video 12).
//   measure(text, face, size, tracking?) -> px width, SYNCHRONOUS (shared/metrics.generated.ts: the faces' own advance
//       widths, written by fetch_fonts.py), so a label fits its box on every frame (no measureText race).
//   fitSize(text, face, maxPx, maxW) -> the largest size <= maxPx that fits maxW.
//   <Rich text .../>  sets a verified string, DRAWING what no face carries: '^NN' -> a raised smaller exponent ('1.4 × 10^32 K'
//       shows 10 with a raised '32'; '^' is never set), '≈' -> an SVG double tilde (placard 5), '~' -> a TALL drawn tilde
//       (QA B2: the fonts' shallow '~' read as a minus at phone scale). Everything else is set.
//   <Sci mantissa exp unit size/>  the same exponent drawing as a component ('1.4 × 10' + raised '32' + ' K').
//   <Label/>: the look's small data label (IBM Plex Mono, Ash / Bone), variants plain / chip (Forge glass) / probably
//       (outline + hatch, the PROBABLY grammar). No face carries '→': draw arrows with shared/Icons.tsx <Arrow>.
//   <RungLabel/>: the hero rung label (Saira Condensed 700 number + IBM Plex Mono description) on its gravity seat.
// No hooks here (pure components).

import React from "react";
import { C, FONT, rgba } from "../theme";
import { METRICS } from "./metrics.generated";

export type Face = "display" | "mono" | "monoMed";

/** advance width in px of `text` set in `face` at `size` px (+ `tracking` px between glyphs); '^' and '≈' as drawn by <Rich> */
export const measure = (text: string, face: Face, size: number, tracking = 0) => {
  const m = METRICS[face];
  let w = 0;
  let sup = false;
  for (const ch of text) {
    if (ch === "^") {
      sup = true;
      continue;
    }
    if (sup && !/[0-9]/.test(ch)) sup = false;
    if (ch === "≈") w += 0.62;
    else if (ch === "~") w += 0.52;
    else w += (m.adv[ch] ?? m.space) * (sup ? SUP_SCALE : 1);
  }
  return w * size + tracking * Math.max(0, [...text].length - 1);
};
/** vertical metrics in px: cap height, ascent, descent */
export const vmetrics = (face: Face, size: number) => ({ cap: METRICS[face].cap * size, asc: METRICS[face].asc * size, desc: METRICS[face].desc * size });
/** the largest size <= maxPx (in 0.5 px steps) at which `text` fits `maxW` */
export const fitSize = (text: string, face: Face, maxPx: number, maxW: number, tracking = 0) => {
  let s = maxPx;
  while (s > 8 && measure(text, face, s, tracking) > maxW) s -= 0.5;
  return s;
};

export const FACE_CSS: Record<Face, { fontFamily: string; fontWeight: number }> = {
  display: { fontFamily: FONT.display, fontWeight: 700 },
  mono: { fontFamily: FONT.mono, fontWeight: 400 },
  monoMed: { fontFamily: FONT.mono, fontWeight: 500 },
};

export const hatch = (color: string, alpha = 0.25, gap = 7) =>
  `repeating-linear-gradient(45deg, ${rgba(color, alpha)} 0 1.5px, transparent 1.5px ${gap}px)`;

/** the exponent: SUP_SCALE of the size, raised SUP_RAISE of the size */
export const SUP_SCALE = 0.58;
export const SUP_RAISE = 0.42;

/** an inline SVG '≈' (two stacked tildes) at the current font size */
const Approx: React.FC<{ size: number; color: string }> = ({ size, color }) => {
  const w = size * 0.56;
  const h = size * 0.5;
  const sw = Math.max(1.5, size * 0.075);
  const wave = (y: number) => `M ${sw} ${y} C ${w * 0.3} ${y - h * 0.22}, ${w * 0.45} ${y + h * 0.22}, ${w * 0.62} ${y} S ${w - sw} ${y - h * 0.14}, ${w - sw} ${y - h * 0.14}`;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: "inline-block", verticalAlign: "middle", margin: `0 ${size * 0.03}px` }}>
      <path d={wave(h * 0.38)} stroke={color} strokeWidth={sw} fill="none" strokeLinecap="round" />
      <path d={wave(h * 0.72)} stroke={color} strokeWidth={sw} fill="none" strokeLinecap="round" />
    </svg>
  );
};

/** an inline SVG '~' with a TALL wave (QA B2: the fonts' shallow tilde reads as a minus at phone scale) */
const Tilde: React.FC<{ size: number; color: string }> = ({ size, color }) => {
  const w = size * 0.5;
  const h = size * 0.62;
  const sw = Math.max(1.6, size * 0.085);
  const y = h * 0.52;
  const a = size * 0.13;
  const d = `M ${sw} ${y + a * 0.3} C ${w * 0.22} ${y - a * 1.6}, ${w * 0.42} ${y - a}, ${w * 0.5} ${y} S ${w * 0.78} ${y + a * 1.6}, ${w - sw} ${y - a * 0.3}`;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: "inline-block", verticalAlign: "middle", margin: `0 ${size * 0.02}px 0 0`, position: "relative", top: -size * 0.06 }}>
      <path d={d} stroke={color} strokeWidth={sw} fill="none" strokeLinecap="round" />
    </svg>
  );
};

/** a verified string with its drawn parts ('^NN' raised exponent, '≈' tilde pair); inherits font / colour from the parent */
export const Rich: React.FC<{ text: string; size: number; color?: string }> = ({ text, size, color = "currentColor" }) => {
  const parts: React.ReactNode[] = [];
  const re = /\^([0-9]+)|≈|~/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let k = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) parts.push(<React.Fragment key={k++}>{text.slice(last, m.index)}</React.Fragment>);
    if (m[0] === "≈") parts.push(<Approx key={k++} size={size} color={color === "currentColor" ? C.bone : color} />);
    else if (m[0] === "~") parts.push(<Tilde key={k++} size={size} color={color === "currentColor" ? C.bone : color} />);
    else
      parts.push(
        <span key={k++} style={{ fontSize: size * SUP_SCALE, position: "relative", top: -size * SUP_RAISE, lineHeight: 0 }}>
          {m[1]}
        </span>,
      );
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(<React.Fragment key={k++}>{text.slice(last)}</React.Fragment>);
  return <>{parts}</>;
};

/** '1.4 × 10' + a raised '32' + ' K' (any mantissa / exponent / unit) in Saira Condensed 700 */
export const Sci: React.FC<{ mantissa: string; exp: string; unit?: string; size: number; color?: string; opacity?: number }> = ({
  mantissa, exp, unit = "", size, color = C.bone, opacity = 1,
}) => (
  <span style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: size, lineHeight: 1, color, opacity, whiteSpace: "nowrap" }}>
    {mantissa}
    <span style={{ fontSize: size * SUP_SCALE, position: "relative", top: -size * SUP_RAISE, lineHeight: 0 }}>{exp}</span>
    {unit}
  </span>
);

/** A small label on the stage (absolute px, vertically centred on y). */
export const Label: React.FC<{
  x: number; y: number; text: string; size?: number; color?: string; opacity?: number; anchor?: "left" | "center" | "right";
  variant?: "plain" | "chip" | "probably"; weight?: 400 | 500;
}> = ({ x, y, text, size = 26, color = C.bone, opacity = 1, anchor = "left", variant = "plain", weight = 400 }) => {
  const tx = anchor === "left" ? "0" : anchor === "center" ? "-50%" : "-100%";
  const box: React.CSSProperties =
    variant === "plain"
      ? { textShadow: "0 2px 8px rgba(11,9,7,0.8)" }
      : {
          padding: "3px 12px", borderRadius: variant === "probably" ? 18 : 6, backgroundColor: rgba(C.forge, 0.76),
          border: variant === "probably" ? `1.5px solid ${rgba(C.bone, 0.9)}` : "none",
          backgroundImage: variant === "probably" ? hatch(C.bone, 0.16) : undefined,
        };
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(${tx}, -50%)`, fontFamily: FONT.mono, fontWeight: weight,
      fontSize: size, lineHeight: 1.15, color, opacity, whiteSpace: "nowrap", ...box }}>
      <Rich text={text} size={size} color={color} />
    </div>
  );
};

/** The hero rung label: number (Saira Condensed 700, `size`) over its description (IBM Plex Mono 400, `labelSize`), left
 *  edge at x, the NUMBER's centre line at y; `dy` = the gravity drop from T.seat(...).y, `opacity` likewise. */
export const RungLabel: React.FC<{
  x: number; y: number; num: string; label?: string; size?: number; labelSize?: number; color?: string; labelColor?: string;
  opacity?: number; dy?: number; anchor?: "left" | "right";
}> = ({ x, y, num, label, size = 96, labelSize = 34, color = C.bone, labelColor = C.ash, opacity = 1, dy = 0, anchor = "left" }) => (
  <div style={{ position: "absolute", left: x, top: y + dy, transform: `translate(${anchor === "right" ? "-100%" : "0"}, ${-size * 0.55}px)`, opacity,
    textAlign: anchor, whiteSpace: "nowrap" }}>
    <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: size, lineHeight: 1.1, color, textShadow: "0 4px 18px rgba(11,9,7,0.7)" }}>
      <Rich text={num} size={size} color={color} />
    </div>
    {label ? <div style={{ fontFamily: FONT.mono, fontWeight: 400, fontSize: labelSize, lineHeight: 1.2, color: labelColor, marginTop: size * 0.02 }}>{label}</div> : null}
  </div>
);
