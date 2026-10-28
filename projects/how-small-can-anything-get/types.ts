// Shapes of artifacts/props.json (written by build_props.py). All frames are ABSOLUTE @ 30 fps.
// Video 17 "How Small Can Anything Get?" / the SCALE WELL: video 16's ladder engine flipped DOWNWARD in metres
// (L = -log10(metres); the rail never moves, no camera).

export type SectionId = "s1" | "s2" | "s3" | "s4" | "s5";
export type SceneId =
  | "sc01" | "sc02" | "sc03" | "sc04" | "sc05" | "sc06"
  | "sc07" | "sc08" | "sc09" | "sc10" | "sc11" | "sc12";
export type RungId = "sand" | "hair" | "cell" | "virus" | "atom" | "proton";
export type MediaId = "S1" | "S2" | "S3" | "ATOM";

export type Word = { section: string; text: string; f0: number; f1: number };
export type Window_ = { id: string; from: number; durationInFrames: number };
export type SceneWindow = Window_ & { section: string };

/** no caption tones in this film (plain only) */
export type CaptionTone = "plain";
export type CaptionWord = { text: string; f0: number; f1: number; line: number; tone: CaptionTone };
export type CaptionPage = { section: string; startFrame: number; exitFrame: number; words: CaptionWord[] };

export type MeterState = "IDLE" | "MEASURED" | "PROBABLY" | "MAYBE";
/** repeat = same state as the previous key (a new claim of the same grade): the tab pulses instead of gliding */
export type MeterKey = { frame: number; glideStart: number; state: MeterState; sublabel: string; section: string; anchor: string; claim: string; repeat: boolean };

export type Rect = { x0: number; x1: number; y0: number; y1: number };

/**
 * A RUNG (shared/Ladder.tsx draws it): its tick drops onto y = railY(L) and its label chip (`lines`: 'NAME · number' or the
 * name over the number) SEATS on `seat` (gravity drop, T.seat) WITH the marker's arrival (lessons 33 / 46). `metres` is the
 * brief's value; L = -log10(metres) (the brief's placement).
 */
export type Rung = { id: RungId; name: string; num: string; lines: string[]; metres: number; L: number; seat: number };

/**
 * THE LADDER (per-frame root curves; arrays have total_frames entries).
 *   markerL   the marker's L (descending rung by rung on eased moves: first moving frame = descend*, landing ON *Seat)
 *   markerVis 0..1;  railDraw 0..1 the rail drawing bright top -> bottom (X1 on railDraw)
 *   veil      0..0.2 the faint veil dimming the rail below YOUR EYE (from eyeLine, for the rest of the film)
 */
export type LadderInfo = { markerL: number[]; markerVis: number[]; railDraw: number[]; veil: number[]; rungs: Rung[]; markerR: number; notes: string };

/** a dashed REFERENCE line across the rail (not a rung): draw 0..1 lands ON its key frame; label lines left of the rail */
export type RefLine = { id: "eye" | "micro"; L: number; lines: string[]; draw: number[]; at: number };

/** the ROOT devices below the proton (sc08 ->) and the readout (sc10 ->) */
export type Devices = {
  refs: RefLine[];
  /** sc08: the bracket under the rail bottom + the open downward arrow + 'ELECTRON' (alpha), the sub-label SEATS on `subSeat` */
  electron: { alpha: number[]; name: string; sub: string; subSeat: number };
  /** sc09: the rail BREAK (zigzag) draw 0..1 from breakDraw */
  brk: number[];
  /** sc09 ->: the dashed violet PLANCK line (alpha, in ON planckIn), brightened ON floorGlow (glow 0..1) + 'a floor? unproven' */
  planck: { y: number; alpha: number[]; glow: number[]; label: string; floor: string; floorSeat: number };
  /** sc10 ->: the readout; count = glyphs shown of `text` (1 on readoutStart ... all ON readoutEnd); `lines` = its wrap */
  readout: { count: number[]; alpha: number[]; text: string; lines: string[] };
  /** sc07: the note in the window under the drawn atom (seats ON nucleusPulse); `pulse` = the nucleus pulse's peak frame */
  atomNote: { lines: string[]; seat: number; alpha: number[]; pulse: number };
};

/** THE ZEROS COUNTER (root): zeros after the decimal point of the active rung's metres; steps ON `ticks` */
export type CounterInfo = { value: number[]; alpha: number[]; ticks: number[]; label: string };

/** a state of the root WINDOW: an AI plate (`base` = public/ path) or the DRAWN atom (`base` = null) */
export type WindowPlate = {
  id: MediaId;
  scene: string;
  alpha: number[];
  push: [number, number];
  pushFrom: number;
  pushTo: number;
  tag: string;
  base: string | null;
  placeholder: boolean;
};
export type WindowInfo = { box: Rect; radius: number; frame: number; open: number[]; plates: WindowPlate[] };

export type Placard = {
  enter: number;
  exit: number;
  line: string;
  lines: string[];
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
  railDraw: number;
  sandSeat: number;
  sandTicks: number[];
  windowOpen1: number;
  descendHair: number;
  hairSeat: number;
  hairTicks: number[];
  eyeLine: number;
  plateSwap1: number;
  descendCell: number;
  cellSeat: number;
  cellTicks: number[];
  plateSwap2: number;
  descendVirus: number;
  virusSeat: number;
  virusTicks: number[];
  lightLine: number;
  windowClose1: number;
  windowOpen2: number;
  descendAtom: number;
  atomSeat: number;
  atomTicks: number[];
  nucleusPulse: number;
  descendProton: number;
  protonSeat: number;
  protonTicks: number[];
  windowClose2: number;
  electronIn: number;
  noSize: number;
  breakDraw: number;
  planckIn: number;
  spinStart: number;
  spinEnd: number;
  spinTicks: number[];
  readoutStart: number;
  readoutEnd: number;
  readoutTicks: number[];
  floorGlow: number;
  closingStart: number;
  wayFrame: number;
  wayEndFrame: number;
  chordFrame: number;
  ctaFrame: number;
};

export type Motion = { SEAT_F: number; WINDOW_OPEN_F: number; WINDOW_CLOSE_F: number; XFADE_F: number; CLIMB_F: number; BEAM_F: number; TICK_STEP_F: number; FADE_F: number };

/** verified root strings (scene_plan.metadata.verified_on_screen_strings) */
export type Labels = { axis: string; zeros: string; ai: string; drawn: string };

export type ScaleProps = {
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
  ladder: LadderInfo;
  devices: Devices;
  counter: CounterInfo;
  window: WindowInfo;
  placards: Placard[];
  labels: Labels;
  cta: { text: string; lines: string[]; frame: number };
  /** the finished-line ending: from `from` (= the release of 'one.') every channel is constant */
  settle: { from: number; freezeFrom: number; chordFrame: number };
  freezes: { from: number; to: number }[];
  audio: AudioFrames;
  motion: Motion;
  layers: "all" | "picture";
  exportVariant: "main" | "loop";
};

/** Props every scene component receives from the root. Frames are absolute. */
export type SceneProps = { from: number; to: number };

/** How long a scene stays mounted around its window, and its stacking order (higher draws on top). */
export type Mount = { pre: number; post: number; z: number };
