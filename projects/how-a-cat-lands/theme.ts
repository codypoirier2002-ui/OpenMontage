// Design tokens for "How Does a Cat Always Land on Its Feet?" / "Operating Theatre, re-dressed as a test lab" (video 15).
// art-direction.md + scene_plan.metadata are the source of truth (palette, typography, safe_areas, signature_device).
// Copied from projects/how-a-mosquito-drinks/theme.ts (video 14, QA passed): the same four faces, self-hosted.
//
// Fonts are loaded ONCE here, at module scope, self-hosted: fetch_fonts.py copied the exact woff2 files
// @remotion/google-fonts would request into public/fonts/ (from video 14), and we hand the package's own metadata (getInfo,
// imported from the package's ES-module build, verified by fetch_fonts.py) to its from-info loader with staticFile() URLs.
// Glyphs (fetch_fonts.py asserts every verified on-screen string + placard in Plex Sans Condensed 600 / 700 AND Roboto Mono
// 400 / 500): É · ~ % : ( ) ' - ? and the digits are in every face; NO face carries → ≈ ✓: arrows and check marks are SVG
// (shared/Icons.tsx <Arrow>, <ArrowLabel>, <CheckMark>) and '~' is drawn TALL by shared/Type.tsx <Rich>.
//
// COLOUR RULES (art direction; asserted in review): FRONT amber (C.front) ONLY on the cat's front half (its tint, its dial
// arc / needle, the dial label 'FRONT') and the caption word 'front'; BACK cyan (C.back) ONLY on the back half (tint, dial,
// 'BACK') and the caption word 'back' (s3 only). Stamp red (C.stamp) ONLY on the stamps ('IMPOSSIBLE?', 'NOT ALWAYS').
// Everything else is steel, ink, ledger paper or slate. No tray, no skin, no blood, no saliva (video 14's devices are gone).

import { Easing, staticFile } from "remotion";
import { getInfo as plexInfo } from "@remotion/google-fonts/IBMPlexSansCondensed";
import { getInfo as monoInfo } from "@remotion/google-fonts/RobotoMono";
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

const plex = selfHosted(plexInfo(), "normal", ["600", "700"], "latin");
const mono = selfHosted(monoInfo(), "normal", ["400", "500"], "latin");
const bricolage = selfHosted(bricolageInfo(), "normal", ["800"], "latin");
const spline = selfHosted(splineInfo(), "normal", ["600"], "latin");

/** CSS font-family stacks (only these weights are loaded). */
export const FONT = {
  /** IBM Plex Sans Condensed 600 / 700: the dial labels 'FRONT' / 'BACK' (>= 28 px), the stamps, the ledger's big figures,
   *  labels, placards (600) */
  display: `'${plex}', 'Arial Narrow', sans-serif`,
  /** Roboto Mono 400 / 500: 'PROCEDURE: LANDING', the checklist rows, the ELAPSED clock, readouts ('total spin: 0'), the ledger
   *  rows, honesty tags (>= 24 px) */
  mono: `'${mono}', monospace`,
  /** Bricolage Grotesque 800: captions + the settle CTA (channel standard) */
  caption: `'${bricolage}', sans-serif`,
  /** Spline Sans Mono 600: the honesty tab (channel standard) */
  tab: `'${spline}', monospace`,
} as const;

/** scene_plan.metadata.palette (+ derived tints, named). */
export const C = {
  // channel
  nightInk: "#0A0B10", // caption slab + tab glass
  bone: "#F4EFE6", // caption + tab text
  // the look: a slate test lab
  drape: "#3B4A55", // Drape (slate): the ground
  drapeDeep: "#2C3740", // the drape's folds / vignette
  drapeLit: "#4A5C68", // the lab light's pool on the drape
  steel: "#C9D1D3", // the rig, the cat's outline, the dials
  steelLit: "#E6ECED", // steel highlight
  steelEdge: "#8E9A9D", // steel edges, the window frame
  shadow: "#1C2B2A", // shadows, chips, ink
  front: "#E8A33D", // ONLY the front half (+ 'FRONT' / the caption word 'front')
  frontLit: "#F2BE6A", // the front amber lightened for text on the dark slab (caption tone 'front')
  back: "#6CC6D9", // ONLY the back half (+ 'BACK' / the caption word 'back')
  backLit: "#93D8E6", // the back cyan lightened for the slab (caption tone 'back')
  stamp: "#C8473B", // Stamp red: ONLY the stamps
  paper: "#F3F1EA", // Ledger Paper: the checklist card + the ledger card
  paperInk: "#1C2B2A", // card text
  paperFaint: "#8A938F", // card secondary text ('illustrative', the ghost column)
  tickInk: "#2C3740", // the drawn check marks (drape deep)
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

/** Motion language (art-direction 'Motion': intensity 4; the fall is a gravity ease-in; each half follows ONE smooth angle
 *  curve shared by its silhouette and its dial; stamps / the ledger seat with gravity drops on their sounds). */
export const E = {
  drop: Easing.in(Easing.quad), // stamps, the ledger card FALL and seat (still moving on seat - 1: lesson 22)
  open: Easing.out(Easing.quad), // the window opens (first visible frame ON its key frame)
  calm: Easing.inOut(Easing.sin), // fades, pushes
  meter: Easing.bezier(0.7, 0, 0.3, 1), // honesty capsule glide, 12 f
} as const;

/** Layout (scene_plan.metadata.safe_areas, as built), 1080x1920. Nothing textual at y >= 1574 or x >= 929, nothing above y 192.
 *  build_props.py asserts the boxes below against its own constants (CARD / WIN / FIELD / DIALS / LEDGER / FLOOR_Y). */
export const L = {
  W: 1080,
  H: 1920,
  topUi: 192,
  stage: { y0: 320, y1: 1100 },
  /** the header 'PROCEDURE: LANDING' (root, Roboto Mono 500), top-left beside the card */
  header: { x: 140, y: 232, size: 30 },
  /** THE RIG (root): the steel rail across the field top, the release clamp hanging from it at clampX */
  rig: { x0: 140, x1: 600, railY: 312, clampX: 380, jawY: 392 },
  /** THE CAT FIELD (units draw the cat + insets here; the floor line at floorY from sc09) */
  field: { x0: 120, x1: 620, y0: 360, y1: 1000, floorY: 960 },
  /** THE CHECKLIST CARD (root, seated from frame 0) */
  card: { x0: 640, x1: 920, y0: 220, y1: 600, r: 14 },
  /** THE WINDOW (root): ONE portrait box for S1, the Marey strip and S2, left of the card (never over it) */
  win: { x0: 160, x1: 620, y0: 360, y1: 1000, r: 22, frame: 6 },
  /** THE DIALS column (units mount <DialsLive/>): FRONT and BACK protractors + 'total spin: 0' */
  dials: { x0: 640, x1: 920, y0: 620, y1: 860, r: 56, frontX: 712, backX: 850, cy: 742, labelY: 652, readoutY: 826 },
  /** THE LEDGER card (sc11-sc12, units mount <Ledger/>): the counted columns left, the hatched ghost column right */
  ledger: { x0: 140, x1: 920, y0: 630, y1: 1010, ghostX0: 652 },
  /** the root 'drawn · not to scale' tag (the drawn cat + rig), bottom-left under the field */
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

/** Ambient: grain 2 % (+ the drape's static weave 3 % luma). */
export const AMBIENT = { grain: 0.02, weave: 0.03 } as const;
