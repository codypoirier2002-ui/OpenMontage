// Shapes of artifacts/props.json (written by build_props.py). All frames are ABSOLUTE @ 30 fps.
// Video 19 "How Long Can Anything Last?" / the LIFESPAN COLUMN: video 18's ladder engine pointing UP in years
// (L = log10(years); the rail never moves, no camera).

export type SectionId = "s1" | "s2" | "s3" | "s4" | "s5";
export type SceneId =
  | "sc01" | "sc02" | "sc03" | "sc04" | "sc05" | "sc06"
  | "sc07" | "sc08" | "sc09" | "sc10" | "sc11" | "sc12";
export type RungId = "mayfly" | "you" | "tortoise" | "shark" | "pine" | "sun" | "dwarf" | "proton";
export type MediaId = "S1" | "S2" | "S3" | "SUN" | "TANK";

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
 * A RUNG (shared/Ladder.tsx draws it): its tick drops onto y = railY(L) and its label chip (`lines`: 'NAME · number', or the
 * name over the number (over a third line)) SEATS on `seat` (gravity drop, T.seat) WITH the marker's arrival (lessons 33 / 46).
 * `years` is the brief's value; L = log10(years) (the brief's placement). `open` = a LOWER LIMIT (the PROTON): its tick is dashed
 * and an arrow points up from it.
 */
export type Rung = { id: RungId; name: string; num: string; lines: string[]; years: number; L: number; seat: number; open?: boolean };

/**
 * THE LADDER (per-frame root curves; arrays have total_frames entries).
 *   markerL   the marker's L (climbing rung by rung on eased moves: first moving frame = climb*, landing ON *Seat)
 *   markerVis 0..1 (a ghost ~0.3 from foreverDraw: the story has left the rungs, lesson 60)
 *   railDraw  0..1 the rail drawing bright bottom -> top from railDraw
 */
export type LadderInfo = { markerL: number[]; markerVis: number[]; railDraw: number[]; rungs: Rung[]; markerR: number; notes: string };

/** the ROOT devices and the window's drawn insets */
export type Devices = {
  /** sc09: the rail BREAK (zigzag above the proton) draw 0..1 from breakDraw */
  brk: number[];
  /** sc12: the dashed 'forever?' line rising through the break (draw 0..1 from foreverDraw); its label seats ON labelSeat */
  forever: { draw: number[]; label: string; labelSeat: number };
  /** sc10 ->: the readout; count = glyphs shown of `text` (1 on readoutStart ... all ON readoutEnd); `lines` = its wrap; alpha fades out before the MAYBE glide */
  readout: { count: number[]; alpha: number[]; text: string; lines: string[] };
  /** sc06-sc07: the drawn Sun (always) and red dwarf (alpha, in ON dwarfIn) inside the window; lifetimes seat ON their seats */
  sun: { dwarfAlpha: number[]; names: string[]; lifetimes: string[]; sunSeat: number; dwarfSeat: number };
  /** sc08-sc11: the drawn detector tank; its note seats ON noteSeat */
  tank: { note: string; noteSeat: number };
};

/** THE ZEROS COUNTER (root): the power of ten of the active rung's years; steps ON `ticks` */
export type CounterInfo = { value: number[]; alpha: number[]; ticks: number[]; label: string };

/** a state of the root WINDOW: an AI plate (`base` = public/ path) or a DRAWN inset (`base` = null) */
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
  mayflySeat: number;
  mayflyTicks: number[];
  climbYou: number;
  youSeat: number;
  youTicks: number[];
  windowOpen1: number;
  climbTortoise: number;
  tortoiseSeat: number;
  tortoiseTicks: number[];
  plateSwap1: number;
  climbShark: number;
  sharkSeat: number;
  plateSwap2: number;
  climbPine: number;
  pineSeat: number;
  pineTicks: number[];
  windowClose1: number;
  windowOpen2: number;
  climbSun: number;
  sunSeat: number;
  sunTicks: number[];
  dwarfIn: number;
  climbDwarf: number;
  dwarfSeat: number;
  dwarfTicks: number[];
  windowClose2: number;
  windowOpen3: number;
  noDecay: number;
  climbProton: number;
  spinStart: number;
  protonSeat: number;
  spinEnd: number;
  spinTicks: number[];
  breakDraw: number;
  readoutStart: number;
  readoutEnd: number;
  readoutTicks: number[];
  closingStart: number;
  foreverDraw: number;
  windowClose3: number;
  foreverSeat: number;
  releaseFrame: number;
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
  /** the finished-line ending: from `from` (= the release of 'forever.') every channel is constant */
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
