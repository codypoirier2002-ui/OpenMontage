// Design tokens for "How Fast Can Anything Go?" / "Speed Ladder" (video 16: video 13's ladder engine re-dressed; NO
// black-body colour). art-direction.md + scene_plan.metadata are the source of truth (palette, typography, safe_areas,
// signature_device). Pattern of projects/how-a-cat-lands/theme.ts (video 15, QA passed) + projects/how-hot-can-it-get/theme.ts.
//
// Fonts are loaded ONCE here, at module scope, self-hosted: fetch_fonts.py fetched the exact woff2 files
// @remotion/google-fonts would request into public/fonts/ (fonts.gstatic.com, the package's own URLs), and we hand the
// package's own metadata (getInfo, imported from the package's ES-module build, verified by fetch_fonts.py) to its from-info
// loader with staticFile() URLs. The render browser never touches the network.
// Glyphs (fetch_fonts.py asserts every verified on-screen string + placard in Saira Condensed 600 / 700 AND IBM Plex Mono
// 400 / 500): · ~ % : ( ) ' - × ° = / and the digits are in every face; IBM Plex Mono's zero is SLASHED (asserted);
// NO face carries → ≈ ✓: arrows are SVG (shared/Icons.tsx <Arrow>, <ArrowLabel>) and '~' is drawn TALL by shared/Type.tsx <Rich>.
//
// COLOUR RULES (art direction; asserted in review): the Marker white-cyan (C.marker) ONLY on the moving marker, its streaks
// and the light beam; Wall red (C.wall) ONLY on the 'c' line, its 'c' label and the gap bracket's tick on it. Everything
// else is steel / bone / night ink / the chip colour. No temperature colours anywhere.

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
  /** Saira Condensed 600 / 700: rung NAMES ('WALK', 'FALCON (dive)', >= 28 px), the YOU tag, 'ENERGY NEEDED', 'LHC protons',
   *  the placards (600) */
  display: `'${saira}', 'Arial Narrow', sans-serif`,
  /** IBM Plex Mono 400 / 500 (slashed zeros): rung NUMBERS, decade ticks, the ZEROS counter, the LHC readout, 'km/h · log
   *  scale', honesty tags (>= 24 px) */
  mono: `'${plex}', monospace`,
  /** Bricolage Grotesque 800: captions + the settle CTA (channel standard) */
  caption: `'${bricolage}', sans-serif`,
  /** Spline Sans Mono 600: the honesty tab (channel standard) */
  tab: `'${spline}', monospace`,
} as const;

/** scene_plan.metadata.palette (+ derived tints, named). */
export const C = {
  // channel
  nightInk: "#0A0B10", // caption slab + tab glass
  bone: "#F4EFE6", // caption + tab text, rung names
  // the look: a night-ink sky, a steel rail, ONE white-cyan accent, ONE red line
  skyTop: "#070A12", // Night Ink (sky gradient top)
  skyBottom: "#0D1424", // Night Ink (sky gradient bottom)
  steel: "#AEB8C2", // Steel: the rail, ticks, labels, fine print
  steelDim: "#6B7681", // Steel dimmed: decade ticks + their numbers, unlit rail
  marker: "#BFF6FF", // Marker white-cyan: ONLY the marker, its streaks, the light beam
  wall: "#E5484D", // Wall red: ONLY the 'c' line, its label and the gap bracket's tick on it
  chip: "#141B2B", // Chip / card: rung label chips, the readout card, the counter chip
  shadow: "#0E1320", // tag chips (Tag.tsx), label backplates
  paper: "#141B2B", // Type.tsx Label 'paper' variant (unused here): the chip colour
  paperInk: "#F4EFE6", // ... with bone ink
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

/** Motion language (art-direction: intensity 4; the marker climbs on smooth eases; rung labels / chips seat with gravity
 *  drops on their sounds; the light beam races; the asymptotic creep slows without end). */
export const E = {
  drop: Easing.in(Easing.quad), // labels, chips, the readout card FALL and seat (still moving on seat - 1: lesson 22)
  open: Easing.out(Easing.quad), // the window opens (first visible frame ON its key frame)
  calm: Easing.inOut(Easing.sin), // fades, pushes, the marker's climbs
  meter: Easing.bezier(0.7, 0, 0.3, 1), // honesty capsule glide, 12 f
} as const;

/** Layout (scene_plan.metadata.safe_areas, as built), 1080x1920. Nothing textual at y >= 1574 or x >= 929 (text ends <= 912),
 *  nothing above y 192. build_props.py asserts the boxes below against its own constants (RAIL / WIN / COUNTER / READOUT). */
export const L = {
  W: 1080,
  H: 1920,
  topUi: 192,
  stage: { y0: 320, y1: 1100 },
  /** THE RAIL (root, shared/Ladder.tsx): a log10(km/h) axis on the spine at x 250: y(L) = axisY0 - L * ppd, L = 0 (1 km/h) at
   *  axisY0 (y 1080) up to L_c = log10(1,079,252,849) = 9.03313 at cY (y 380) = THE 'c' LINE. Decade ticks x 236-264 with their
   *  numbers right-aligned at numRight (mono 18 px); rung ticks x 232-268; rung label chips from labelX. */
  rail: { x: 250, axisY0: 1080, cY: 380, ppd: 700 / 9.03313, tickX0: 236, tickX1: 264, rungX0: 232, rungX1: 268, labelX: 280, numRight: 224, labelMaxRight: 912 },
  /** 'km/h · log scale' under the rail's foot */
  axisLabel: { x: 140, y: 1100 },
  /** THE WINDOW (root): ONE portrait box for S1 / S2 / S3, right of the rung labels (never over them: build_props asserts) */
  win: { x0: 580, x1: 920, y0: 440, y1: 893, r: 22, frame: 6 },
  /** THE ZEROS COUNTER (root, shared/Counter.tsx): a chip right-aligned at x 920, top right */
  counter: { x0: 640, x1: 920, y0: 220, y1: 340, digitPx: 72, labelPx: 22 },
  /** the YOU tag (units: <YouTagLive/>), LEFT of the rail at the rung it sits on (its right edge at numRight) */
  you: { right: 224, h: 36 },
  /** the orbit inset (U1, sc05): the window's column while the window is closed */
  orbit: { x0: 600, x1: 920, y0: 460, y1: 800 },
  /** 'anything with mass' label (U2, sc09-sc10): right of the marker */
  massLabel: { x: 280 },
  /** THE ENERGY NEEDED bar (U2, sc10): a column right of the rung labels' field, growing from the rail's foot off the top */
  energy: { barX0: 600, barX1: 660, y0: 1080, curve: { x0: 690, x1: 920, y0: 440, y1: 640 } },
  /** THE LHC READOUT card (U2, sc11-sc12): where the window was (closed from sc08) */
  readout: { x0: 600, x1: 920, y0: 460, y1: 600, r: 14 },
  /** the gap bracket (root): a tiny bracket on the rail's left between 'c' and the marker; 'the gap' right-aligned at numRight */
  gap: { x: 240, labelRight: 224 },
  /** the kit's root DrawnTag position (NOT mounted in this film: every drawing carries its own tag; kept for the kit contract) */
  drawnTag: { x: 140, y: 1066 },
  placard: { x: 140, y: 1124, w: 772, h: 80 },
  tab: { x: 140, y: 1236, w: 488, h: 54 },
  /** the honesty sublabel chip, right of the tab (unused by this plan; kept for the channel-standard tab) */
  sublabel: { x: 640, y: 1242, w: 272, h: 42 },
  slab: { x: 140, y: 1296, w: 800, h: 192, textX: 168, textRight: 912 },
  textRight: 912,
  bottomUi: 1574,
  rightRail: 929,
} as const;

/** screen y of log10(km/h) = Lv on the rail (the rail never moves: no camera) */
export const railY = (Lv: number) => L.rail.axisY0 - Lv * L.rail.ppd;

/** Ambient: grain 2 % + faint star dust in the sky. */
export const AMBIENT = { grain: 0.02, stars: 0.35 } as const;
