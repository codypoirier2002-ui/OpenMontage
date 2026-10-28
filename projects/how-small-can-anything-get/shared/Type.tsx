// KIT TEMPLATE (docs/channel/kit, taken from video 14, QA passed). Copied by new_project.sh; the comments below describe
// video 14 - rewrite them for this video. Contract with theme.ts / time.ts / types.ts: docs/channel/kit/KIT.md.
// Type helpers (pattern of projects/how-hot-can-it-get/shared/Type.tsx, video 13).
//   measure(text, face, size, tracking?) -> px width, SYNCHRONOUS (shared/metrics.generated.ts: the faces' own advance
//       widths, written by fetch_fonts.py), so a label fits its box on every frame (no measureText race).
//   fitSize(text, face, maxPx, maxW) -> the largest size <= maxPx that fits maxW.
//   <Rich text .../>  sets a verified string, DRAWING the '~' TALL (an SVG wave; the fonts' shallow tilde reads as a minus at
//       phone scale: video 13 QA B2). Everything else is set.
//   <Label/>: the look's small data label (Roboto Mono; variants plain / chip (drape glass) / paper (checklist paper) /
//       probably (outline + hatch, the PROBABLY grammar)).
// No face carries '→' / '✓': draw them with shared/Icons.tsx <Arrow> / <CheckMark>.
// No hooks here (pure components).

import React from "react";
import { C, FONT, rgba } from "../theme";
import { METRICS } from "./metrics.generated";

export type Face = "display" | "displaySemi" | "mono" | "monoMed";

/** advance width in px of `text` set in `face` at `size` px (+ `tracking` px between glyphs); '~' as drawn by <Rich> */
export const measure = (text: string, face: Face, size: number, tracking = 0) => {
  const m = METRICS[face];
  let w = 0;
  for (const ch of text) w += ch === "~" ? 0.5 : (m.adv[ch] ?? m.space);
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
  displaySemi: { fontFamily: FONT.display, fontWeight: 600 },
  mono: { fontFamily: FONT.mono, fontWeight: 400 },
  monoMed: { fontFamily: FONT.mono, fontWeight: 500 },
};

export const hatch = (color: string, alpha = 0.25, gap = 7) =>
  `repeating-linear-gradient(45deg, ${rgba(color, alpha)} 0 1.5px, transparent 1.5px ${gap}px)`;

/** an inline SVG '~' with a TALL wave (the fonts' shallow tilde reads as a minus at phone scale) */
export const Tilde: React.FC<{ size: number; color: string }> = ({ size, color }) => {
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

/** a verified string with its drawn '~'; inherits font / colour from the parent */
export const Rich: React.FC<{ text: string; size: number; color?: string }> = ({ text, size, color = "currentColor" }) => {
  const parts: React.ReactNode[] = [];
  let last = 0;
  let k = 0;
  for (let i = 0; i < text.length; i++) {
    if (text[i] !== "~") continue;
    if (i > last) parts.push(<React.Fragment key={k++}>{text.slice(last, i)}</React.Fragment>);
    parts.push(<Tilde key={k++} size={size} color={color === "currentColor" ? C.bone : color} />);
    last = i + 1;
  }
  if (last < text.length) parts.push(<React.Fragment key={k++}>{text.slice(last)}</React.Fragment>);
  return <>{parts}</>;
};

/** A small label on the stage (absolute px, vertically centred on y). */
export const Label: React.FC<{
  x: number; y: number; text: string; size?: number; color?: string; opacity?: number; anchor?: "left" | "center" | "right";
  variant?: "plain" | "chip" | "paper" | "probably"; weight?: 400 | 500; dy?: number;
}> = ({ x, y, text, size = 26, color, opacity = 1, anchor = "left", variant = "plain", weight = 400, dy = 0 }) => {
  const tx = anchor === "left" ? "0" : anchor === "center" ? "-50%" : "-100%";
  const ink = color ?? (variant === "paper" ? C.paperInk : C.bone);
  const box: React.CSSProperties =
    variant === "plain"
      ? { textShadow: "0 2px 8px rgba(28,43,42,0.55)" }
      : variant === "paper"
        ? { padding: "4px 12px", borderRadius: 8, backgroundColor: C.paper, boxShadow: "0 6px 16px rgba(28,43,42,0.35)" }
        : {
            padding: "4px 12px", borderRadius: variant === "probably" ? 18 : 8, backgroundColor: rgba(C.shadow, 0.82),
            border: variant === "probably" ? `1.5px solid ${rgba(C.bone, 0.9)}` : "none",
            backgroundImage: variant === "probably" ? hatch(C.bone, 0.16) : undefined,
          };
  return (
    <div style={{ position: "absolute", left: x, top: y + dy, transform: `translate(${tx}, -50%)`, fontFamily: FONT.mono, fontWeight: weight,
      fontSize: size, lineHeight: 1.15, color: ink, opacity, whiteSpace: "nowrap", ...box }}>
      <Rich text={text} size={size} color={ink} />
    </div>
  );
};

// ---- video 17: powers of ten -------------------------------------------------------------------------------------------
// No face carries the superscripts ⁻ ⁴-⁹ ⁰ (fetch_fonts.py / build_props.py): <Sci> sets every run of superscript characters
// as RAISED text in the parent's face at max(24, 0.72 * size) px (never under 24 px, lesson 31); everything else through <Rich>.
const SUP: Record<string, string> = { "⁻": "−", "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9" };
export const supSize = (size: number) => Math.max(24, Math.round(size * 0.72));

export const Sci: React.FC<{ text: string; size: number; color?: string }> = ({ text, size, color = "currentColor" }) => {
  const runs: { sup: boolean; s: string }[] = [];
  for (const ch of text) {
    const sup = ch in SUP;
    const last = runs[runs.length - 1];
    if (last && last.sup === sup) last.s += sup ? SUP[ch] : ch;
    else runs.push({ sup, s: sup ? SUP[ch] : ch });
  }
  return (
    <>
      {runs.map((r, i) =>
        r.sup ? (
          <span key={i} style={{ fontSize: supSize(size), position: "relative", top: -size * 0.4, marginLeft: 1, letterSpacing: -0.5 }}>{r.s}</span>
        ) : (
          <Rich key={i} text={r.s} size={size} color={color} />
        ),
      )}
    </>
  );
};
