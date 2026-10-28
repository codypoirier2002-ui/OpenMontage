// Design tokens for "How Long Can Anything Last?" / the LIFESPAN COLUMN (video 19: the ladder engine of videos 16-18, pointing UP in
// years on a log scale). art-direction.md is the source of truth. Pattern of projects/how-heavy-can-anything-get/theme.ts (video 18).
//
// Fonts are loaded ONCE here, at module scope, self-hosted (fetch_fonts.py fetched the exact woff2 files into public/fonts/).
// Glyphs: NO face carries the superscripts: every power of ten is DRAWN as raised text >= 24 px (shared/Type.tsx <Sci>);
// '~' is drawn tall by <Rich>; > < ? · are in every face.
//
// COLOUR RULES: the white-cyan marker (C.marker) ONLY on the marker; the Sun / red dwarf tints (C.sun, C.dwarf) ONLY on the two
// discs drawn inside the window's Sun inset; no red anywhere else. Everything else steel / bone / ink / chip.

import { Easing, staticFile } from "remotion";
import { getInfo as sairaInfo } from "@remotion/google-fonts/SairaCondensed";
import { getInfo as plexInfo } from "@remotion/google-fonts/IBMPlexMono";
import { getInfo as bricolageInfo } from "@remotion/google-fonts/BricolageGrotesque";
import { getInfo as splineInfo } from "@remotion/google-fonts/SplineSansMono";
import { loadFontFromInfo } from "@remotion/google-fonts/from-info";

type FontInfo = Parameters<typeof loadFontFromInfo>[0];

const selfHosted = (info: FontInfo, style: "normal" | "italic", weights: string[], subset: string): string => {
  const files: Record<string, Record<string, string>> = {};
  for (const w of weights) {
    if (!info.fonts[style]?.[w]?.[subset]) throw new Error(`theme.ts: ${info.fontFamily} has no ${style} ${w} '${subset}'`);
    files[w] = { [subset]: staticFile(`fonts/${info.importName}-${style}-${w}-${subset}.woff2`) };
  }
  const local: FontInfo = {
    ...info,
    fonts: { [style]: files },
    unicodeRanges: { [subset]: info.unicodeRanges[subset] },
    subsets: [subset],
  };
  return loadFontFromInfo(local, style, { weights, subsets: [subset] }).fontFamily;
};

const saira = selfHosted(sairaInfo(), "normal", ["600", "700"], "latin");
const plex = selfHosted(plexInfo(), "normal", ["400", "500"], "latin");
const bricolage = selfHosted(bricolageInfo(), "normal", ["800"], "latin");
const spline = selfHosted(splineInfo(), "normal", ["600"], "latin");

/** CSS font-family stacks (only these weights are loaded). */
export const FONT = {
  /** Saira Condensed 600 / 700: rung NAMES (28 px), 'forever?', the placards (600) */
  display: `'${saira}', 'Arial Narrow', sans-serif`,
  /** IBM Plex Mono 400 / 500 (slashed zeros): rung NUMBERS (26 px), powers, the ZEROS counter, the axis label, tags (>= 24 px) */
  mono: `'${plex}', monospace`,
  /** Bricolage Grotesque 800: captions + the settle CTA (channel standard) */
  caption: `'${bricolage}', sans-serif`,
  /** Spline Sans Mono 600: the honesty tab (channel standard) */
  tab: `'${spline}', monospace`,
} as const;

/** the palette (+ derived tints, named). */
export const C = {
  // channel
  nightInk: "#0A0B10", // caption slab + tab glass
  bone: "#F4EFE6", // caption + tab text, rung names
  // the look: ink slightly lighter at the top, a steel rail, ONE white-cyan marker
  skyTop: "#0B0E16", // ink (background gradient top)
  skyBottom: "#05060A", // ink (background gradient bottom)
  steel: "#AEB8C2", // the rail, ticks, labels, fine print
  steelDim: "#6B7681", // decade ticks + powers, the unlit rail, the reference lines
  marker: "#BFF6FF", // white-cyan: ONLY the marker (+ glow)
  sun: "#FFE3A3", // the drawn Sun disc only (window inset)
  dwarf: "#D9654A", // the drawn red dwarf disc only (window inset)
  chip: "#121722", // chips: rung labels, the readout card, the counter chip
  shadow: "#0E1320", // tag chips (Tag.tsx), label backplates
  paper: "#121722", // Type.tsx Label 'paper' variant (unused)
  paperInk: "#F4EFE6",
} as const;

/** Smoked glass (slab, tab, placards): Night Ink at `alpha` + 10 px blur. */
export const glass = (alpha = 0.62) => ({
  backgroundColor: `rgba(10, 11, 16, ${alpha})`,
  backdropFilter: "blur(10px)",
  WebkitBackdropFilter: "blur(10px)",
});

/** rgba() from a palette hex. */
export const rgba = (hex: string, a: number) => {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  return `rgba(${r},${g},${b},${a})`;
};

/** Motion language (intensity 4): the marker climbs on smooth eases; chips seat with gravity drops on their sounds. */
export const E = {
  drop: Easing.in(Easing.quad), // labels, chips FALL and seat (still moving on seat - 1: lesson 22)
  open: Easing.out(Easing.quad),
  calm: Easing.inOut(Easing.sin),
  meter: Easing.bezier(0.7, 0, 0.3, 1), // honesty capsule glide, 12 f
} as const;

/** Layout, 1080x1920. Nothing textual at y >= 1574 or x >= 929 (text ends <= 912), nothing above y 192. build_props.py
 *  asserts the boxes below against its own constants (RAIL / WIN / COUNTER / READOUT). */
export const L = {
  W: 1080,
  H: 1920,
  topUi: 192,
  /** THE RAIL (root, shared/Ladder.tsx): L = log10(years) on the spine at x 250, UPWARD: y(L) = y1 - (L - L0) * ppd, L -4 (about an
   *  hour) at y 1020 up to L 33 (10^33 yr, the proton's lower limit) at y 500. Ticks every 3 powers x 236-264 with their powers
   *  right-aligned at numRight; rung ticks x 232-268; rung label chips from labelX. Above y 500 the rail BREAKS (zigzag y 432-458)
   *  and a dashed 'forever?' line continues up to y 240. */
  rail: { x: 250, y0: 500, y1: 1020, L0: -4, L1: 33, ppd: 520 / 37, tickX0: 236, tickX1: 264, rungX0: 232, rungX1: 268, labelX: 280, numRight: 224, labelMaxRight: 572,
    breakY0: 432, breakY1: 458, arrowTip: 468, foreverY0: 424, foreverY1: 240 },
  /** 'years · log scale' under the rail's bottom, left */
  axisLabel: { x: 100, y: 1064 },
  /** the 'forever?' label at the top of the dashed line */
  forever: { x: 280, y: 206 },
  /** THE WINDOW (root): ONE portrait box for S1 / S2 / S3 and the drawn Sun inset / detector tank */
  win: { x0: 580, x1: 920, y0: 440, y1: 893, r: 22, frame: 6 },
  /** THE ZEROS COUNTER (root): a chip right-aligned at x 920, top right */
  counter: { x0: 640, x1: 920, y0: 220, y1: 340, digitPx: 72, labelPx: 24 },
  /** sc10-sc11: THE READOUT card ('1' + 33 zeros + ' yr') under the open window, in the window's column */
  readout: { x0: 580, x1: 920, y0: 930, y1: 1060, r: 14, px: 26 },
  /** the kit's root DrawnTag position (NOT mounted in this film) */
  drawnTag: { x: 140, y: 1066 },
  placard: { x: 140, y: 1124, w: 772, h: 80 },
  tab: { x: 140, y: 1236, w: 488, h: 54 },
  sublabel: { x: 640, y: 1242, w: 272, h: 42 },
  slab: { x: 140, y: 1296, w: 800, h: 192, textX: 168, textRight: 912 },
  textRight: 912,
  bottomUi: 1574,
  rightRail: 929,
} as const;

/** screen y of L = log10(years) on the rail (the rail never moves: no camera) */
export const railY = (Lv: number) => L.rail.y1 - (Lv - L.rail.L0) * L.rail.ppd;

/** Ambient: grain 2 % + faint dust. */
export const AMBIENT = { grain: 0.02, stars: 0.18 } as const;
