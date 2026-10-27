// Shapes of artifacts/props.json (written by build_props.py). All frames are ABSOLUTE @ 30 fps.
// Copied from projects/how-a-mosquito-drinks/types.ts (video 14, QA passed) and re-dressed for the test lab.

export type SectionId = "s1" | "s2" | "s3" | "s4" | "s5";
export type SceneId =
  | "sc01" | "sc02" | "sc03" | "sc04" | "sc05" | "sc06"
  | "sc07" | "sc08" | "sc09" | "sc10" | "sc11" | "sc12";
export type MediaId = "S1" | "A1" | "S2";
export type RowId = "01" | "02" | "03" | "04" | "05" | "06";

export type Word = { section: string; text: string; f0: number; f1: number };
export type Window_ = { id: string; from: number; durationInFrames: number };
export type SceneWindow = Window_ & { section: string };

/** front = the word 'front' (s3, FRONT amber); back = the word 'back' in 'the back half' (s3, BACK cyan); else Bone.
 *  s4's 'back arched' is the cat's spine, not the back half: plain (the colour rules). */
export type CaptionTone = "plain" | "front" | "back";
export type CaptionWord = { text: string; f0: number; f1: number; line: number; tone: CaptionTone };
export type CaptionPage = { section: string; startFrame: number; exitFrame: number; words: CaptionWord[] };

export type MeterState = "IDLE" | "MEASURED" | "PROBABLY" | "MAYBE";
/** repeat = same state as the previous key (a new claim of the same grade): the tab pulses instead of gliding */
export type MeterKey = { frame: number; glideStart: number; state: MeterState; sublabel: string; section: string; anchor: string; claim: string; repeat: boolean };

export type Rect = { x0: number; x1: number; y0: number; y1: number };

/**
 * THE CAT (engine: shared/Cat.tsx; curves: build_props.py). One value per frame for each channel (length total_frames).
 * Units mount <CatLive/> (or <Cat pose={T.cat(f)}/>) in EVERY scene they own; the pose is never re-authored in a scene, so
 * the sc06 -> sc07 seam (u1 -> u2) matches by construction.
 *   x, y        the waist (the joint between the halves), frame px
 *   front, back each half's ROLL about its own long axis, degrees: 0 = upside down (legs up), 180 = feet down. The two curves
 *               conserve 'spin' by construction: I_front * dFront + I_back * dBack = 0 on every frame (I = 1 legs out,
 *               0.1 legs tucked), so the 'total spin: 0' readout is literally true of the drawing
 *   frontTuck, backTuck  0 = legs out, 1 = legs tucked
 *   bend        the V at the waist, degrees (0 = straight)
 *   arch        0..1 the landing arch (sc09);  flex 0..1 the landing squash
 *   vis         0..1 opacity;  ghost 0..1 (1 = outline only, no tint: sc01's frozen preview and sc10's short-drop demo)
 */
export type CatCurves = {
  x: number[]; y: number[]; front: number[]; back: number[]; frontTuck: number[]; backTuck: number[];
  bend: number[]; arch: number[]; flex: number[]; vis: number[]; ghost: number[]; scale: number;
};
export type CatPose = {
  x: number; y: number; front: number; back: number; frontTuck: number; backTuck: number;
  bend: number; arch: number; flex: number; vis: number; ghost: number; scale: number;
};

/** THE DIALS (shared/Dials.tsx): visibility per frame; their needles read the cat's own front / back curves. */
export type DialCurves = { front: number[]; back: number[]; total: number[] };

/** THE RIG (root; shared/Rig.tsx): the steel rail + release clamp (open 0..1) + the floor line (vis 0..1, y). */
export type RigInfo = { clamp: number[]; floor: number[]; floorY: number; header: string; drawnTag: number[] };

/**
 * THE CHECKLIST CARD (root; shared/Checklist.tsx): seated from frame 0; each row's check mark draws over TICK_F frames and
 * COMPLETES ON its `tick` frame (X4 there). clock[f] = ELAPSED seconds (illustrative; '0.00 s'), stopped from `clockStop`.
 */
export type ChecklistRow = { id: RowId; text: string; tick: number };
export type ChecklistInfo = {
  seat: number;
  header: string;
  rows: ChecklistRow[];
  tickF: number;
  clock: number[];
  clockStop: number;
  clockLabel: string;
  clockNote: string;
};

/**
 * THE WINDOW (root; shared/Window.tsx): ONE box (L.win) shared by every plate. open[f] = the window frame's visibility
 * (first visible frame ON its key frame). Each plate has alpha[f] (crossfades); the TAG shown is the plate with the larger
 * alpha (a HARD swap at the crossfade midpoint, lesson 38). A1 is the Marey film strip: cells[] stacked vertically, step[f] =
 * the cell index at the top of the window (eased moves).
 */
export type WindowPlate = {
  id: MediaId;
  scene: string;
  alpha: number[];
  push: [number, number];
  pushFrom: number;
  pushTo: number;
  tag: string;
  base: string | null;
  cells?: string[];
  step?: number[];
};
export type WindowInfo = { box: Rect; radius: number; frame: number; open: number[]; plates: WindowPlate[] };

export type Placard = {
  enter: number;
  exit: number;
  line: string;
  lines: string[];
  /** IBM Plex Sans Condensed 600 px, the largest that fits the rail (measured in build_props.py) */
  size: number;
  w: number;
  fine: string | null;
  fineSize: number | null;
  fineW: number | null;
  anchor: string;
};

/** THE KEY FRAMES (build_soundtrack.py K -> soundtrack_report.json 'frames'): every SFX is ON its frame. */
export type AudioFrames = {
  soundtrack: string;
  clampOpen: number;
  previewFlipEnd: number;
  windowOpen1: number;
  readouts: number[];
  plateSwap: number;
  stripSteps: number[];
  stampImpossible: number;
  windowClose1: number;
  catReset: number;
  clockStart: number;
  innerEar: number;
  tick01: number;
  bendStart: number;
  bendSeat: number;
  dialsIn: number;
  totalSeat: number;
  tick02: number;
  tuckStart: number;
  tuckSeat: number;
  turnStart: number;
  tick03: number;
  turnEnd: number;
  armsIn: number;
  swapStart: number;
  backTurnStart: number;
  tick04: number;
  swapEnd: number;
  floorIn: number;
  tick05: number;
  arch: number;
  land: number;
  tick06: number;
  windowOpen2: number;
  windowClose2: number;
  dialsOut: number;
  stampNotAlways: number;
  shortStart: number;
  shortTurn: number;
  shortGone: number;
  ledgerSeat: number;
  barFrom: number;
  barTo: number;
  closingStart: number;
  ghostColumn: number;
  notCounted: number;
  bracket: number;
  vetFrame: number;
  vetEndFrame: number;
  chordFrame: number;
  ctaFrame: number;
};

/** motion constants (build_soundtrack.py; build_props.py asserts) */
export type Motion = { SEAT_F: number; WINDOW_OPEN_F: number; WINDOW_CLOSE_F: number; XFADE_F: number; STRIP_STEP_F: number; STRIP_MOVE_F: number; TICK_F: number; TWIST_F: number };

/** verified root strings (scene_plan.metadata.verified_on_screen_strings) the builders may reuse */
export type Labels = {
  drawn: string; ai: string; marey: string; illustrative: string; elapsed: string; header: string;
  front: string; back: string; total: string; up: string;
};

export type CatProps = {
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
  cat: CatCurves;
  dials: DialCurves;
  rig: RigInfo;
  checklist: ChecklistInfo;
  window: WindowInfo;
  placards: Placard[];
  labels: Labels;
  cta: { text: string; lines: string[]; frame: number };
  /** the finished-line ending: from `from` (= the release of 'vet.') every channel is constant; every ambient clock is
   * periodic to `freezeFrom` and reads frame 0's values from it (T.loopFrame) */
  settle: { from: number; freezeFrom: number; chordFrame: number };
  freezes: { from: number; to: number }[];
  audio: AudioFrames;
  motion: Motion;
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
