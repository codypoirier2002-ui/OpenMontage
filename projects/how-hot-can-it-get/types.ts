// Shapes of artifacts/props.json (written by build_props.py). All frames are ABSOLUTE @ 30 fps.

export type SectionId = "s1" | "s2" | "s3" | "s4" | "s5";
export type SceneId =
  | "sc01" | "sc02" | "sc03" | "sc04" | "sc05" | "sc06" | "sc07"
  | "sc08" | "sc09" | "sc10" | "sc11" | "sc12" | "sc13";
export type RungId = "dv" | "venus" | "suncore" | "kstar" | "lhc" | "planck";
export type MarkId = "draper" | "sunsurface" | "converge";
export type MediaId = "K1" | "S2" | "K2" | "S4";

export type Word = { section: string; text: string; f0: number; f1: number };
export type Window_ = { id: string; from: number; durationInFrames: number };
export type SceneWindow = Window_ & { section: string };

/** heat = a spoken NUMBER word: the current black-body colour (lifted for contrast; before the glow the 1,800 K filament
 * amber); ice = 'floor:' (the cold-floor callback); else Bone */
export type CaptionTone = "plain" | "heat" | "ice";
export type CaptionWord = { text: string; f0: number; f1: number; line: number; tone: CaptionTone };
export type CaptionPage = { section: string; startFrame: number; exitFrame: number; words: CaptionWord[] };

export type MeterState = "IDLE" | "MEASURED" | "PROBABLY" | "MAYBE";
/** repeat = same state as the previous key (a new claim of the same grade): the tab pulses instead of gliding */
export type MeterKey = { frame: number; glideStart: number; state: MeterState; sublabel: string; section: string; anchor: string; claim: string; repeat: boolean };

export type Rect = { x0: number; x1: number; y0: number; y1: number };

/**
 * THE GLOW (per-frame root schedule; arrays have total_frames entries). shared/GlowField.tsx draws it.
 *   k   the temperature (kelvin) whose black-body colour the frame glows (shared/blackbody.ts bbRgb(k))
 *   i   intensity 0..1. EXACTLY 0 while k < DRAPER_K (sc01-sc04: nothing that cool glows); the sc05 sweep rolls k from
 *       Venus (737 K) to the Sun's core (15 million degC) on T.sfx.sweepStart -> T.sfx.sunCoreSeat; afterwards the colour
 *       holds (k keeps climbing with the rungs, but past ~40,000 K the colour no longer changes); from 'So' (s5) it eases
 *       to the low settle intensity, constant through the settle (lesson 25)
 */
export type GlowInfo = { k: number[]; i: number[]; iMax: number; iSettle: number; slabClamp: number; notes: string };

/**
 * THE LADDER RAIL (per-frame root schedule; shared/Ladder.tsx). A log10(kelvin) axis on the spine at x 180:
 *   y(L, f) = axisY0 + camY[f] - (L - lo[f]) * ppd[f]   (L = log10 T in K; the axis runs from axisY0 up to topY)
 *   camY  the sc02 tilt (the floor slides down), back to 0 in sc03
 *   lo / ppd  the visible log range (zooms out with the sc05 sweep, re-scales for KSTAR, compresses in sc08, drifts up to
 *         the Planck view in sc10; constant from there)
 *   floor 0..1 the ice floor hairline drawing (sc01); the floor is NOT on the log axis (0 K is -infinity): a fixed
 *         callback at floorY + camY, below a break mark
 *   spine 0..1 the dashed spine drawing floor -> '?' (sc02)
 *   fray  0..1 the rail above the Planck mark fraying into a broken dash ('breaks', sc11)
 *   q / qAlpha  the filament '?' draw progress / opacity (draws sc02, dims to half sc10, fades out sc12)
 *   cursor 0..1 the glowing bead that rides the rail at log10(glow.k) during the sweep (sc05)
 *   chip   0..1 the 'black-body colour' swatch chip (from the sweep to the end)
 */
export type RailInfo = {
  lo: number[]; ppd: number[]; camY: number[]; floor: number[]; spine: number[]; fray: number[]; q: number[]; qAlpha: number[];
  cursor: number[]; chip: number[]; compactVis: number[];
  axisY0: number; topY: number; floorY: number; x: number; qX: number; qY: number; qK: number; notes: string;
};

/** a rung: seated (tick drops in) ON `seat`; its compact number shows while compactVis[f] > 0 and f >= compactFrom */
export type Rung = { id: RungId; kelvin: number; L: number; num: string; label: string; seat: number; compactFrom: number; glows: boolean };
/** a rail mark (dashed line + label): fades in from `at` */
export type Mark = { id: MarkId; kelvin: number; L: number; text: string; at: number };

/** the zeros counter chip ('12 zeros' at the LHC rung -> '32 zeros' at the Planck mark): value / alpha / anchor L per frame */
export type ZerosInfo = { value: number[]; alpha: number[]; L: number[]; seat: number; ticks: number[] };

/** a plate in the root WINDOW. Visible from `from` (crossfading in over xf when it follows another plate) to `to` + xf. */
export type WindowMedia = {
  id: MediaId;
  kind: "clip" | "still";
  src: string;
  /** the staged first frame (shown before `start`) and, for a held clip, the last one */
  first: string;
  last: string;
  frames: number;
  /** forward: frame (f - start) clamped to the last staged frame (then held); still: the image */
  mode: "forward" | "still";
  start: number;
  from: number;
  to: number;
  xf: number;
  /** slow push (scale about the window centre) from `from` to `to` + xf */
  push: [number, number];
  fit: { w: number; h: number; scale: number; left: number; top: number; anchor: number[]; at: number[] };
  tag: string;
  srcRange30: [number, number];
};
/** the root WINDOW: open 0..1 (scale + fade), dim 0..1 (Forge Black over the plate for drawings), lut 0..1 (the labelled
 * thermal false-colour view, sc03 only) */
export type WindowInfo = { box: Rect; radius: number; open: number[]; dim: number[]; lut: number[]; media: WindowMedia[]; lutTag: string };

export type Placard = {
  enter: number;
  exit: number;
  line: string;
  lines: string[];
  /** Saira Condensed 700 px, the largest that fits the rail (measured in build_props.py) */
  size: number;
  w: number;
  fine: string | null;
  fineSize: number | null;
  fineW: number | null;
  anchor: string;
};

export type AudioFrames = {
  soundtrack: string;
  ember: number;
  floorDraw: number;
  floorLabelSeat: number;
  camTilt: number;
  qStart: number;
  spineStart: number;
  windowOpen: number;
  dvSeat: number;
  lutOn: number;
  venusXfade: number;
  venusSeat: number;
  draperMark: number;
  leadMelt: number;
  windowClose1: number;
  sweepStart: number;
  sunCoreSeat: number;
  windowOpen2: number;
  kstarSeat: number;
  timerArc: number;
  colliderXfade: number;
  beamFlash: number;
  compress: number;
  lhcGroupSeats: number[];
  lhcSeat: number;
  soupStart: number;
  protonMelt: number;
  windowClose2: number;
  drift: number;
  planckMark: number;
  zeroTicks: number[];
  sciWrite: number;
  fray: number;
  closingStart: number;
  qFade: number;
  knowFrame: number;
  knowEndFrame: number;
  chordFrame: number;
  ctaFrame: number;
};

export type HotProps = {
  timeline: {
    fps: number;
    width: number;
    height: number;
    total_frames: number;
    lead_frames: number;
    sections: Window_[];
    scenes: SceneWindow[];
    words: Word[];
  };
  captionPages: CaptionPage[];
  meter: MeterKey[];
  glow: GlowInfo;
  rail: RailInfo;
  rungs: Rung[];
  marks: Mark[];
  zeros: ZerosInfo;
  window: WindowInfo;
  placards: Placard[];
  /** root label strings (verified): floor, log scale, chip, Planck mark, fray */
  labels: { floor: string; floorValue: string; logScale: string; chip: string; planck: string; fray: string; zerosUnit: string };
  cta: { text: string; lines: string[]; frame: number };
  /** the finished-line ending: from `from` (= the release of 'know.') every channel is constant; every ambient clock is
   * periodic to `freezeFrom` and reads frame 0's values from it (T.loopFrame) */
  settle: { from: number; freezeFrom: number; chordFrame: number };
  freezes: { from: number; to: number }[];
  audio: AudioFrames;
  /** "picture" renders the picture layer only (no overlay plane) */
  layers: "all" | "picture";
  exportVariant: "main" | "loop";
};

/** Props every scene component receives from the root. Frames are absolute. */
export type SceneProps = {
  /** first frame of this scene's window (its boundary with the previous scene) */
  from: number;
  /** first frame AFTER this scene's window (the next scene's boundary) */
  to: number;
};

/** How long a scene stays mounted around its window, and its stacking order (higher draws on top). */
export type Mount = { pre: number; post: number; z: number };
