// Shapes of artifacts/props.json (written by build_props.py). All frames are ABSOLUTE @ 30 fps.
// Video 18 "How Heavy Can Anything Get?" / the WEIGHT COLUMN: video 17's ladder engine pointing UP in kilograms
// (L = log10(kg); the rail never moves, no camera).

export type SectionId = "s1" | "s2" | "s3" | "s4" | "s5";
export type SceneId =
  | "sc01" | "sc02" | "sc03" | "sc04" | "sc05" | "sc06"
  | "sc07" | "sc08" | "sc09" | "sc10" | "sc11" | "sc12";
export type RungId = "you" | "whale" | "eiffel" | "humans" | "earth" | "sun" | "neutron" | "sgra";
export type MediaId = "S1" | "S2" | "S3" | "BH";

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
 * name over the number, or the name over the number split in two) SEATS on `seat` (gravity drop, T.seat) WITH the marker's
 * arrival (lessons 33 / 46). `kg` is the brief's value; L = log10(kg) (the brief's placement).
 */
export type Rung = { id: RungId; name: string; num: string; lines: string[]; kg: number; L: number; seat: number };

/**
 * THE LADDER (per-frame root curves; arrays have total_frames entries).
 *   markerL   the marker's L (climbing rung by rung on eased moves: first moving frame = climb*, landing ON *Seat)
 *   markerVis 0..1 (a ghost ~0.3 from universeIn: the story has left the rungs, lesson 60)
 *   railDraw  0..1 the rail drawing bright bottom -> top from railDraw
 */
export type LadderInfo = { markerL: number[]; markerVis: number[]; railDraw: number[]; rungs: Rung[]; markerR: number; notes: string };

/** the ROOT devices (sc08 ->) */
export type Devices = {
  /** sc09: the dashed 'Mercury's orbit' circle around the drawn black hole (draw 0..1 from orbitDraw; the label seats ON labelSeat).
   *  horizon = the black disc's radius as a fraction of the orbit's radius (~24 / 116 million km) */
  orbit: { draw: number[]; label: string; labelSeat: number; horizon: number };
  /** sc10: the rail BREAK (zigzag above the rail's top) draw 0..1 from breakDraw */
  brk: number[];
  /** sc10 ->: the dashed OBSERVABLE UNIVERSE line (alpha, first visible ON universeIn) and its two label lines */
  universe: { alpha: number[]; lines: string[] };
  /** sc10 ->: the LINEAR comparison: the amber ordinary bar (ordAlpha, in ON universeIn), the violet dark bar (rise 0..1, lands
   *  ON darkSeat at `ratio` x the ordinary bar's height) and its labels ('~5 : 1 · inferred' seats ON darkSeat) */
  bars: { ordAlpha: number[]; rise: number[]; ratio: number; ordLabel: string; darkLabel: string; ratioLabel: string; tag: string; seat: number };
};

/** THE ZEROS COUNTER (root): the power of ten of the active rung's kilograms; steps ON `ticks` */
export type CounterInfo = { value: number[]; alpha: number[]; ticks: number[]; label: string };

/** a state of the root WINDOW: an AI plate (`base` = public/ path) or the DRAWN black hole (`base` = null) */
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
  youSeat: number;
  youTicks: number[];
  windowOpen1: number;
  climbWhale: number;
  whaleSeat: number;
  whaleTicks: number[];
  plateSwap: number;
  climbEiffel: number;
  eiffelSeat: number;
  eiffelTicks: number[];
  windowClose1: number;
  climbHumans: number;
  humansSeat: number;
  humansTicks: number[];
  climbEarth: number;
  earthSeat: number;
  earthTicks: number[];
  climbSun: number;
  sunSeat: number;
  sunTicks: number[];
  windowOpen2: number;
  neutronSeat: number;
  windowClose2: number;
  windowOpen3: number;
  climbSgra: number;
  sgraSeat: number;
  sgraTicks: number[];
  orbitDraw: number;
  windowClose3: number;
  breakDraw: number;
  universeIn: number;
  spinStart: number;
  spinEnd: number;
  spinTicks: number[];
  darkRise: number;
  darkSeat: number;
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
