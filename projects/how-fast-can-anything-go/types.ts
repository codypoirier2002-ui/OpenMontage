// Shapes of artifacts/props.json (written by build_props.py). All frames are ABSOLUTE @ 30 fps.
// Pattern of projects/how-a-cat-lands/types.ts (video 15, QA passed) + projects/how-hot-can-it-get/types.ts (the ladder),
// re-dressed for the Speed Ladder (no black-body, no camera: the rail never moves).

export type SectionId = "s1" | "s2" | "s3" | "s4" | "s5";
export type SceneId =
  | "sc01" | "sc02" | "sc03" | "sc04" | "sc05" | "sc06"
  | "sc07" | "sc08" | "sc09" | "sc10" | "sc11" | "sc12";
export type RungId = "walk" | "cheetah" | "falcon" | "sound" | "earth" | "parker" | "light";
export type MediaId = "S1" | "S2" | "S3";

export type Word = { section: string; text: string; f0: number; f1: number };
export type Window_ = { id: string; from: number; durationInFrames: number };
export type SceneWindow = Window_ & { section: string };

/** this film has no caption tones (the plan: 'plain only'); the kit's TONE / GLOW maps carry the one entry */
export type CaptionTone = "plain";
export type CaptionWord = { text: string; f0: number; f1: number; line: number; tone: CaptionTone };
export type CaptionPage = { section: string; startFrame: number; exitFrame: number; words: CaptionWord[] };

export type MeterState = "IDLE" | "MEASURED" | "PROBABLY" | "MAYBE";
/** repeat = same state as the previous key (a new claim of the same grade): the tab pulses instead of gliding */
export type MeterKey = { frame: number; glideStart: number; state: MeterState; sublabel: string; section: string; anchor: string; claim: string; repeat: boolean };

export type Rect = { x0: number; x1: number; y0: number; y1: number };

/**
 * A RUNG (shared/Ladder.tsx draws it; build_props.py): its tick drops onto y = railY(L) and its label chip (name / number,
 * `lines`) SEATS on `seat` (gravity drop, T.seat), i.e. only when the marker arrives (lessons 33 / 46). `probably` rungs
 * carry the hatched chip 'commonly cited' under the label (the FALCON dive). `kmh` is the brief's number.
 */
export type Rung = { id: RungId; name: string; num: string; lines: string[]; kmh: number; L: number; seat: number; probably: boolean; chip: string | null };

/**
 * THE LADDER (per-frame root curves; arrays have total_frames entries). shared/Ladder.tsx draws them on every frame.
 *   markerL   the marker's position, log10(km/h) (rung by rung: eased climbs; the asymptotic creep toward 'c' from sc09)
 *   markerVis 0..1 the marker's opacity (1 from frame 0)
 *   streak    0..1 the marker's motion intensity (streaks behind it while it climbs; length = log10(speed) px-scaled)
 *   cLit      0.3..1 the red 'c' line's intensity (dim until the light beam reaches it in sc08)
 *   gap       0..1 the gap bracket + 'the gap' (sc11 -> the end)
 *   railDraw  0..1 the rail drawing bright from its foot to 'c' (sc01, X1 whoosh); the dim rail is there from frame 0
 *   The marker NEVER touches 'c': build_props.py asserts railY(markerL) >= cY + MARKER_GAP_PX on every frame.
 */
export type LadderInfo = {
  markerL: number[]; markerVis: number[]; streak: number[]; cLit: number[]; gap: number[]; railDraw: number[];
  rungs: Rung[]; cL: number; markerR: number; gapPx: number; notes: string;
};

/** THE ZEROS COUNTER (root, shared/Counter.tsx): value per frame (0 -> 9 = the order of magnitude of the marker's rung,
 *  i.e. the digits after the first), `ticks` = the frames it steps on (X3 there, except under X2 / X5). */
export type CounterInfo = { value: number[]; alpha: number[]; ticks: number[]; label: string };

/** a plate in the root WINDOW (an AI impression, or its PLACEHOLDER while the still is pending) */
export type WindowPlate = {
  id: MediaId;
  scene: string;
  alpha: number[];
  /** slow push (scale about the window centre) from pushFrom to pushTo */
  push: [number, number];
  pushFrom: number;
  pushTo: number;
  tag: string;
  /** public/ path of the staged plate (stills/<id>.png) */
  base: string;
  /** true while prepare_media.py staged a labelled dark card instead of the real still */
  placeholder: boolean;
};
export type WindowInfo = { box: Rect; radius: number; frame: number; open: number[]; plates: WindowPlate[] };

/** THE YOU TAG (units mount <YouTagLive/>): L = the rung it sits on (WALK -> EARTH on the jump), alpha 0..1 */
export type YouInfo = { L: number[]; alpha: number[]; text: string };
/** THE LIGHT BEAM (units mount <LightBeamLive/>): progress 0..1 up the rail (0 = the foot, 1 = 'c'), alpha 0..1 */
export type BeamInfo = { progress: number[]; alpha: number[] };
/** THE ENERGY NEEDED bar + curve (units mount <EnergyLive/>): vc = v/c, gamma = 1/sqrt(1-vc^2), barH px (runs off the top
 *  on 'end'), alpha 0..1 (gone before the LHC page, lesson 42) */
export type EnergyInfo = { vc: number[]; gamma: number[]; barH: number[]; alpha: number[]; pxPerGamma: number; label: string; axisX: string; axisY: string; tag: string };
/** THE LHC READOUT (units mount <NinesReadoutLive/>): count = glyphs of `value` shown (0..10, one per X3 tick), alpha */
export type NinesInfo = { count: number[]; alpha: number[]; label: string; value: string; ticks: number[]; seat: number };
/** 'anything with mass' (U2, sc09-sc10) and the orbit inset (U1, sc05): root-owned visibilities so the lesson-42 exits are asserted */
export type Fade = { alpha: number[] };

export type Placard = {
  enter: number;
  exit: number;
  line: string;
  lines: string[];
  /** Saira Condensed 600 px, the largest that fits the rail (measured in build_props.py) */
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
  walkSeat: number;
  windowOpen1: number;
  climbCheetah: number;
  cheetahSeat: number;
  cheetahTicks: number[];
  plateSwap: number;
  climbFalcon: number;
  falconSeat: number;
  windowClose1: number;
  climbSound: number;
  soundSeat: number;
  youSeat: number;
  jumpStart: number;
  earthSeat: number;
  earthTicks: number[];
  orbitIn: number;
  orbitOut: number;
  windowOpen2: number;
  probeLabel: number;
  climbParker: number;
  parkerSeat: number;
  fallArrow: number;
  windowClose2: number;
  beamStart: number;
  lightSeat: number;
  lightTicks: number[];
  wallStart: number;
  massLabel: number;
  massOut: number;
  energyIn: number;
  barStart: number;
  barTicks: number[];
  barOff: number;
  energyOut: number;
  readoutSeat: number;
  digitTicks: number[];
  creepEnd: number;
  gapBracket: number;
  closingStart: number;
  wayFrame: number;
  wayEndFrame: number;
  chordFrame: number;
  ctaFrame: number;
};

/** motion constants (build_soundtrack.py; build_props.py asserts) */
export type Motion = { SEAT_F: number; WINDOW_OPEN_F: number; WINDOW_CLOSE_F: number; XFADE_F: number; CLIMB_F: number; BEAM_F: number; TICK_STEP_F: number; FADE_F: number };

/** verified root strings (scene_plan.metadata.verified_on_screen_strings) the builders may reuse */
export type Labels = {
  axis: string; zeros: string; ai: string; drawn: string; c: string; you: string; gap: string; mass: string;
  energy: string; speed: string; energyAxis: string; lhc: string; nines: string; probe: string; falling: string; cited: string;
};

export type SpeedProps = {
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
  counter: CounterInfo;
  window: WindowInfo;
  you: YouInfo;
  beam: BeamInfo;
  energy: EnergyInfo;
  nines: NinesInfo;
  mass: Fade;
  orbit: Fade;
  placards: Placard[];
  labels: Labels;
  cta: { text: string; lines: string[]; frame: number };
  /** the finished-line ending: from `from` (= the release of 'way.') every channel is constant; every ambient clock is
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
