// Timing helpers. EVERY trigger goes through a word, a scene window, a key frame or one of the root curves from the measured
// timeline (artifacts/timeline.json -> props). Never hard-code seconds or frame numbers in a scene. Pattern of
// projects/how-a-cat-lands/time.ts (video 15, QA passed) + projects/how-hot-can-it-get/time.ts (the ladder), re-dressed.
//
//   const T = useT();
//   T.at("s2", "thousand")         -> onset frame of 'thousand,' (case/punctuation-insensitive; nth for repeats)
//   T.end("s5", "way")             -> frame at which 'way.' ends (= T.sfx.wayEndFrame)
//   T.scene("sc05")                -> { from, to, dur };  T.section("s4") -> { from, to, dur }
//   T.sfx.earthSeat ...            -> key frames from build_soundtrack.py (every SFX is already ON its frame)
//   THE LADDER (root curves; shared/Ladder.tsx draws them):
//   T.ladder(frame)                -> { L, y, vis, streak, cLit, gap, railDraw }: the marker's log10(km/h) + screen y, ...
//   T.railY(L)                     -> screen y of log10(km/h) = L (the rail never moves);  T.cY = the 'c' line's y
//   T.rungs / T.rung(id)           -> the rungs (name, num, lines, L, seat, probably, chip)
//   T.counter(frame)               -> { value, alpha }: the ZEROS counter
//   T.win(frame)                   -> the window frame's open 0..1;  T.plate(id, frame) -> the plate's alpha 0..1
//   T.tagAt(frame)                 -> the ONE window tag on screen (the plate with the larger alpha: hard swap, lesson 38)
//   THE DEVICES (units mount the engines from shared/; the SAME curves in every scene, so seams match):
//   T.you(frame)                   -> { L, y, alpha }: the YOU tag;  T.beam(frame) -> { progress, alpha, y }: the light beam
//   T.energy(frame)                -> { vc, gamma, barH, alpha };  T.nines(frame) -> { count, alpha, shown }: the LHC readout
//   T.mass(frame) / T.orbit(frame) -> 0..1: 'anything with mass' / the orbit inset visibilities (the lesson-42 exits)
//   T.seat(frame, seatFrame, n, drop) -> { k, y, opacity, seated, visible }: an element that FALLS (gravity ease-in, still
//                                     moving >= 1 px on seat - 1) and is FULLY SEATED on its seat frame (lessons 4, 22)
//   T.driftFrame(frame)            -> the frame ambient drift should use (no freezes planned: identity)
//   T.loopFrame(frame), T.loopPeriod -> every ambient clock is PERIODIC over loopPeriod (= the release of 'way.') and reads
//                                     frame 0 from it, so the settle is still. Grain / drift seed =
//                                     T.driftFrame(T.loopFrame(frame)) (loopFrame FIRST, lesson 11).

import React, { createContext, useContext } from "react";
import { L as LAYOUT, railY as railYOf } from "./theme";
import type { MediaId, Rung, RungId, SceneId, SectionId, SpeedProps, WindowPlate, Word } from "./types";

const norm = (t: string) => t.toLowerCase().replace(/[^a-z0-9]/g, "");

export type Span = { from: number; to: number; dur: number };
export type LadderState = { L: number; y: number; vis: number; streak: number; cLit: number; gap: number; railDraw: number };

export type Timing = {
  total: number;
  fps: number;
  lead: number;
  word: (section: SectionId, text: string, nth?: number) => Word;
  at: (section: SectionId, text: string, nth?: number) => number;
  end: (section: SectionId, text: string, nth?: number) => number;
  scene: (id: SceneId) => Span;
  section: (id: SectionId) => Span;
  sfx: SpeedProps["audio"];
  motion: SpeedProps["motion"];
  settle: SpeedProps["settle"];
  cta: SpeedProps["cta"];
  labels: SpeedProps["labels"];
  ladder: (frame: number) => LadderState;
  ladderInfo: SpeedProps["ladder"];
  railY: (L: number) => number;
  cY: number;
  rungs: Rung[];
  rung: (id: RungId) => Rung;
  counter: (frame: number) => { value: number; alpha: number };
  counterInfo: SpeedProps["counter"];
  win: (frame: number) => number;
  plate: (id: MediaId, frame: number) => number;
  tagAt: (frame: number) => string | null;
  windowInfo: SpeedProps["window"];
  media: (id: MediaId) => WindowPlate;
  you: (frame: number) => { L: number; y: number; alpha: number };
  beam: (frame: number) => { progress: number; alpha: number; y: number };
  energy: (frame: number) => { vc: number; gamma: number; barH: number; alpha: number };
  energyInfo: SpeedProps["energy"];
  nines: (frame: number) => { count: number; alpha: number; shown: string };
  ninesInfo: SpeedProps["nines"];
  mass: (frame: number) => number;
  orbit: (frame: number) => number;
  seat: (frame: number, seatFrame: number, frames?: number, dropPx?: number) => { k: number; y: number; opacity: number; seated: boolean; visible: boolean };
  freezes: { from: number; to: number }[];
  driftFrame: (frame: number) => number;
  loopFrame: (frame: number) => number;
  loopPeriod: number;
  layers: SpeedProps["layers"];
};

const clamp01 = (x: number) => Math.min(1, Math.max(0, x));

/** per-frame channel, linearly interpolated between frames (fractional frames are allowed) */
export const sample = (arr: number[], frame: number) => {
  const f = Math.max(0, Math.min(arr.length - 1, frame));
  const i = Math.floor(f);
  const j = Math.min(arr.length - 1, i + 1);
  const x = f - i;
  return x > 0 ? arr[i] + (arr[j] - arr[i]) * x : arr[i];
};

export const makeTiming = (p: SpeedProps): Timing => {
  const tl = p.timeline;
  const total = tl.total_frames;
  const word = (section: SectionId, text: string, nth = 1): Word => {
    const hits = tl.words.filter((w) => w.section === section && norm(w.text) === norm(text));
    const w = hits[nth - 1];
    if (!w) throw new Error(`time.ts: no word #${nth} "${text}" in ${section}`);
    return w;
  };
  const span = (list: { id: string; from: number; durationInFrames: number }[], id: string): Span => {
    const s = list.find((x) => x.id === id);
    if (!s) throw new Error(`time.ts: no window ${id}`);
    return { from: s.from, to: s.from + s.durationInFrames, dur: s.durationInFrames };
  };
  const freezes = [...p.freezes].sort((a, b) => a.from - b.from);
  const driftFrame = (frame: number) => {
    let held = 0;
    for (const f of freezes) {
      if (frame >= f.to) held += f.to - f.from;
      else if (frame >= f.from) return f.from - held;
    }
    return frame - held;
  };
  const loopPeriod = p.settle.freezeFrom;
  const loopFrame = (frame: number) => (frame >= loopPeriod ? 0 : frame);
  const plates = Object.fromEntries(p.window.plates.map((m) => [m.id, m])) as Record<MediaId, WindowPlate>;
  const rungs = Object.fromEntries(p.ladder.rungs.map((r) => [r.id, r])) as Record<RungId, Rung>;
  const LD = p.ladder;
  const ladder = (frame: number): LadderState => {
    const Lv = sample(LD.markerL, frame);
    return { L: Lv, y: railYOf(Lv), vis: sample(LD.markerVis, frame), streak: sample(LD.streak, frame), cLit: sample(LD.cLit, frame),
      gap: sample(LD.gap, frame), railDraw: sample(LD.railDraw, frame) };
  };
  // a GRAVITY drop (ease-in, y = -drop * (1 - k^2)) so the element is still visibly moving on seat - 1 (drop 18, 8 f:
  // 4.2 px left to fall) and lands ON the seat frame (the SFX is there; lessons 4, 22)
  const seat = (frame: number, seatFrame: number, frames = 8, dropPx = 18) => {
    const k = clamp01((frame - (seatFrame - frames)) / frames);
    return { k, y: -dropPx * (1 - k * k), opacity: clamp01(k * 1.6), seated: frame >= seatFrame, visible: frame > seatFrame - frames };
  };
  const tagAt = (frame: number) => {
    if (sample(p.window.open, frame) <= 0) return null;
    let best: WindowPlate | null = null;
    let a = 0;
    for (const m of p.window.plates) {
      const v = sample(m.alpha, Math.round(frame));
      if (v > a) {
        a = v;
        best = m;
      }
    }
    return best ? best.tag : null;
  };
  const N = p.nines;
  const nines = (frame: number) => {
    const count = N.count[Math.max(0, Math.min(total - 1, Math.floor(frame)))];
    // the glyph groups: '99.9999991 %' (six nines after the point, lesson 16) lands as 9 | 9. | 9 | 9 | 9 | 9 | 9 | 9 | 1 |  % (10 landings, 12 glyphs)
    const groups = ["9", "9.", "9", "9", "9", "9", "9", "9", "1", " %"];
    return { count, alpha: sample(N.alpha, frame), shown: groups.slice(0, count).join("") };
  };

  return {
    total,
    fps: tl.fps,
    lead: tl.lead_frames,
    word,
    at: (s, t, n) => word(s, t, n).f0,
    end: (s, t, n) => word(s, t, n).f1,
    scene: (id) => span(tl.scenes, id),
    section: (id) => span(tl.sections, id),
    sfx: p.audio,
    motion: p.motion,
    settle: p.settle,
    cta: p.cta,
    labels: p.labels,
    ladder,
    ladderInfo: LD,
    railY: railYOf,
    cY: LAYOUT.rail.cY,
    rungs: LD.rungs,
    rung: (id) => rungs[id],
    counter: (frame) => ({ value: p.counter.value[Math.max(0, Math.min(total - 1, Math.floor(frame)))], alpha: sample(p.counter.alpha, frame) }),
    counterInfo: p.counter,
    win: (frame) => sample(p.window.open, frame),
    plate: (id, frame) => sample(plates[id].alpha, frame),
    tagAt,
    windowInfo: p.window,
    media: (id) => plates[id],
    you: (frame) => {
      const Lv = sample(p.you.L, frame);
      return { L: Lv, y: railYOf(Lv), alpha: sample(p.you.alpha, frame) };
    },
    beam: (frame) => {
      const pr = sample(p.beam.progress, frame);
      return { progress: pr, alpha: sample(p.beam.alpha, frame), y: LAYOUT.rail.axisY0 + (LAYOUT.rail.cY - LAYOUT.rail.axisY0) * pr };
    },
    energy: (frame) => ({ vc: sample(p.energy.vc, frame), gamma: sample(p.energy.gamma, frame), barH: sample(p.energy.barH, frame), alpha: sample(p.energy.alpha, frame) }),
    energyInfo: p.energy,
    nines,
    ninesInfo: N,
    mass: (frame) => sample(p.mass.alpha, frame),
    orbit: (frame) => sample(p.orbit.alpha, frame),
    seat,
    freezes,
    driftFrame,
    loopFrame,
    loopPeriod,
    layers: p.layers,
  };
};

const TimingCtx = createContext<Timing | null>(null);
const CACHE = new WeakMap<SpeedProps, Timing>();
const timingOf = (p: SpeedProps) => {
  let t = CACHE.get(p);
  if (!t) {
    t = makeTiming(p);
    CACHE.set(p, t);
  }
  return t;
};

export const TimingProvider: React.FC<{ props: SpeedProps; children: React.ReactNode }> = ({ props, children }) =>
  React.createElement(TimingCtx.Provider, { value: timingOf(props) }, children);

export const useT = (): Timing => {
  const t = useContext(TimingCtx);
  if (!t) throw new Error("useT() outside <TimingProvider>");
  return t;
};

/** 0..1 progress of `frame` through [a, b], clamped; eased if `ease` is given. */
export const prog = (frame: number, a: number, b: number, ease?: (x: number) => number) => {
  const x = b <= a ? (frame >= b ? 1 : 0) : Math.min(1, Math.max(0, (frame - a) / (b - a)));
  return ease ? ease(x) : x;
};

/** Linear map of `x` from [a0,a1] to [b0,b1], clamped. */
export const remap = (x: number, a0: number, a1: number, b0: number, b1: number) =>
  b0 + (b1 - b0) * Math.min(1, Math.max(0, (x - a0) / (a1 - a0)));

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
