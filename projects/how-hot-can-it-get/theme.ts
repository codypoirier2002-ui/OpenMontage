// Design tokens for "How Hot Can It Get?" / "Black-Body" (art-direction.md + scene_plan.metadata are the source of truth:
// palette, typography, safe_areas, signature_device). Layout conventions mirror
// projects/what-if-earth-stopped-spinning/theme.ts (video 12, delivered, QA passed).
//
// Fonts are loaded ONCE here, at module scope, self-hosted: fetch_fonts.py stored the exact woff2 files
// @remotion/google-fonts would request in public/fonts/, and we hand the package's own metadata (getInfo, imported from the
// package's ES-module build: all four families resolve to dist/esm/<Name>.mjs, verified by fetch_fonts.py) to its
// from-info loader with staticFile() URLs. The render browser never touches the network.
// Glyphs (fetch_fonts.py asserts every verified on-screen string in Saira Condensed 700 AND IBM Plex Mono 400 / 500):
// × ° · ~ > - , ' : and the digits are in every face; NO face carries → or ≈: arrows are SVG (shared/Icons.tsx) and '≈'
// (placard 5) is drawn by shared/Type.tsx <Rich>. The exponent of '1.4 × 10^32 K' is DRAWN as a raised smaller '32'
// (<Rich> / <Sci>): '^' is never set on screen.

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

const saira = selfHosted(sairaInfo(), "normal", ["700"], "latin");
const plex = selfHosted(plexInfo(), "normal", ["400", "500"], "latin");
const bricolage = selfHosted(bricolageInfo(), "normal", ["800"], "latin");
const spline = selfHosted(splineInfo(), "normal", ["600"], "latin");

/** CSS font-family stacks (only these weights are loaded). */
export const FONT = {
  /** Saira Condensed 700: rung numbers ('56.7 °C' 96 px, '> 5,000,000,000,000 K' 88 px, '1.4 × 10' + raised '32' 104 px),
   *  compact rung numbers, placards */
  display: `'${saira}', 'Arial Narrow', sans-serif`,
  /** IBM Plex Mono 400 / 500: rung descriptions, rail marks, tags, chips, 'log scale', the floor label */
  mono: `'${plex}', monospace`,
  /** Bricolage Grotesque 800: captions + the settle CTA (channel standard) */
  caption: `'${bricolage}', sans-serif`,
  /** Spline Sans Mono 600: the honesty tab (channel standard) */
  tab: `'${spline}', monospace`,
} as const;

/** scene_plan.metadata.palette (+ derived tints, named). ALL accent light is the computed black-body ramp
 *  (shared/blackbody.ts), never a palette colour. */
export const C = {
  // channel
  nightInk: "#0A0B10", // caption slab + tab glass
  bone: "#F4EFE6", // caption + tab text
  // the look
  forge: "#0B0907", // Forge Black: the ground
  iron: "#2A211B", // Iron: rail, window frames
  ironLit: "#6B5A4E", // Iron, lit (unlit rung ticks, the spine's dashes, axis ticks): Iron toward Bone
  ash: "#A89A8E", // label grey on forge (rail marks, 'log scale'): Iron toward Bone, more
  ice: "#9FC9DA", // Ice: ONLY the cold-floor callback
  filament: "#FF7F1F", // Filament Warm (1,800 K) = bbHex(1800) rounded: the '?' (the engine computes the exact one)
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

/** Motion language (art-direction 'Motion': intensity 3; rungs seat with gravity drops; the glow sweep is continuous). */
export const E = {
  drop: Easing.in(Easing.quad), // rungs, labels, chips FALL and seat (still moving on seat - 1: lesson 22)
  open: Easing.out(Easing.cubic), // the window opens / closes
  calm: Easing.inOut(Easing.sin), // camera drifts, zooms, fades
  meter: Easing.bezier(0.7, 0, 0.3, 1), // honesty capsule glide, 12 f
} as const;

/** Layout (scene_plan.metadata.safe_areas), 1080x1920. Nothing textual at y >= 1574 or x >= 929, nothing above y 192. */
export const L = {
  W: 1080,
  H: 1920,
  topUi: 192,
  stage: { y0: 320, y1: 1100 },
  /** the ladder rail (spine x 180, the log axis from axisY0 up to topY; the floor callback at floorY) */
  rail: { x: 180, axisY0: 990, topY: 350, floorY: 1060, tickX0: 166, tickX1: 204, labelX: 214 },
  /** the filament '?' (centre of its box) above the rail */
  q: { x: 180, y: 252, h: 118 },
  /** the 'black-body colour' chip (sc05 ->): top band, left */
  chip: { x: 248, y: 210, h: 44 },
  /** THE WINDOW (prepare_media.py WIN; build_props.py asserts) */
  window: { x0: 220, x1: 920, y0: 360, y1: 900, r: 28, frame: 6 },
  placard: { x: 140, y: 1124, w: 772, h: 80 },
  tab: { x: 140, y: 1236, w: 488, h: 54 },
  /** the honesty sublabel chip, right of the tab (unused by this plan; kept for the channel-standard tab) */
  sublabel: { x: 640, y: 1242, w: 272, h: 42 },
  slab: { x: 140, y: 1296, w: 800, h: 192, textX: 168, textRight: 912 },
  textRight: 912,
  bottomUi: 1574,
  rightRail: 929,
} as const;

/**
 * The media fits MEASURED by prepare_media.py (artifacts/media_report.json 'fits'; build_props.py asserts these numbers):
 * the staged source (w x h px) at `scale` frame px per source px; left/top = its top-left in frame px.
 *   K1: horizon (30.8 %) at 45 % down the window (the planned framing; crops the 1.9 px/f near ground).
 *   S2: haze horizon (37.3 %) at 42 % down the window.
 *   K2: the violet loop's centroid at the window centre.   S4: the red module ring's centre at the window centre.
 */
export const FITS = {
  K1: { w: 756, h: 1344, scale: 1, left: 192, top: 189 },
  S2: { w: 756, h: 1344, scale: 1, left: 192, top: 85.8 },
  K2: { w: 778, h: 1382, scale: 1, left: 191.3, top: 8.7 },
  S4: { w: 756, h: 1344, scale: 1, left: 194.5, top: 14.5 },
} as const;

/** Ambient: grain 2.5 % (+ the fine luma dither in GlowField), the forge's iron grain (3 % luma, warm, static). */
export const AMBIENT = { grain: 0.025, iron: 0.03, dither: 0.018 } as const;
