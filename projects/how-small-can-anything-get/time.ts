// Timing helpers. EVERY trigger goes through a word, a scene window, a key frame or one of the root curves from the measured
// timeline (artifacts/timeline.json -> props). Never hard-code seconds or frame numbers in a scene. Pattern of
// projects/how-fast-can-anything-go/time.ts (video 16, QA passed), re-dressed for the Scale Well (video 17).
//
//   const T = useT();
//   T.at("s2", "cell") / T.end("s5", "one")  -> a word's onset / end frame (case/punctuation-insensitive; nth for repeats)
//   T.scene("sc05") / T.section("s4")        -> { from, to, dur }
//   T.sfx.hairSeat ...                       -> key frames from build_soundtrack.py (every SFX is already ON its frame)
//   T.ladder(frame)                          -> { L, y, vis, railDraw, veil }: the marker's L = -log10(m) + screen y
//   T.railY(L)                               -> screen y of L (the rail never moves)
//   T.rungs / T.rung(id)                     -> the rungs (name, num, lines, L, seat)
//   T.counter(frame)                         -> { value, alpha }: the ZEROS counter
//   T.win(frame) / T.plate(id, frame) / T.tagAt(frame)   -> the window's open, a state's alpha, the ONE tag on screen
//   T.dev                                    -> props.devices (refs, electron, brk, planck, readout, atomNote); T.ch(arr, f) samples one
//   T.seat(frame, seatFrame, n, drop)        -> an element that FALLS and is FULLY SEATED on its seat frame (lessons 4, 22)
//   T.loopFrame(frame)                       -> every ambient clock reads frame 0 from the release (the settle is still)

import React, { createContext, useContext } from "react";
import { railY as railYOf } from "./theme";
import type { MediaId, Rung, RungId, SceneId, SectionId, ScaleProps, WindowPlate, Word } from "./types";

const norm = (t: string) => t.toLowerCase().replace(/[^a-z0-9]/g, "");

export type Span = { from: number; to: number; dur: number };
export type LadderState = { L: number; y: number; vis: number; railDraw: number; veil: number };

export type Timing = {
  total: number;
  fps: number;
  lead: number;
  word: (section: SectionId, text: string, nth?: number) => Word;
  at: (section: SectionId, text: string, nth?: number) => number;
  end: (section: SectionId, text: string, nth?: number) => number;
  scene: (id: SceneId) => Span;
  section: (id: SectionId) => Span;
  sfx: ScaleProps["audio"];
  motion: ScaleProps["motion"];
  settle: ScaleProps["settle"];
  cta: ScaleProps["cta"];
  labels: ScaleProps["labels"];
  ladder: (frame: number) => LadderState;
  ladderInfo: ScaleProps["ladder"];
  railY: (L: number) => number;
  rungs: Rung[];
  rung: (id: RungId) => Rung;
  counter: (frame: number) => { value: number; alpha: number };
  counterInfo: ScaleProps["counter"];
  win: (frame: number) => number;
  plate: (id: MediaId, frame: number) => number;
  tagAt: (frame: number) => string | null;
  windowInfo: ScaleProps["window"];
  dev: ScaleProps["devices"];
  ch: (arr: number[], frame: number) => number;
  seat: (frame: number, seatFrame: number, frames?: number, dropPx?: number) => { k: number; y: number; opacity: number; seated: boolean; visible: boolean };
  freezes: { from: number; to: number }[];
  driftFrame: (frame: number) => number;
  loopFrame: (frame: number) => number;
  loopPeriod: number;
  layers: ScaleProps["layers"];
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

export const makeTiming = (p: ScaleProps): Timing => {
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
    return { L: Lv, y: railYOf(Lv), vis: sample(LD.markerVis, frame), railDraw: sample(LD.railDraw, frame), veil: sample(LD.veil, frame) };
  };
  // a GRAVITY drop (ease-in) so the element is still visibly moving on seat - 1 and lands ON the seat frame (lessons 4, 22)
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
    rungs: LD.rungs,
    rung: (id) => rungs[id],
    counter: (frame) => ({ value: p.counter.value[Math.max(0, Math.min(total - 1, Math.floor(frame)))], alpha: sample(p.counter.alpha, frame) }),
    counterInfo: p.counter,
    win: (frame) => sample(p.window.open, frame),
    plate: (id, frame) => sample(plates[id].alpha, frame),
    tagAt,
    windowInfo: p.window,
    dev: p.devices,
    ch: sample,
    seat,
    freezes,
    driftFrame,
    loopFrame,
    loopPeriod,
    layers: p.layers,
  };
};

const TimingCtx = createContext<Timing | null>(null);
const CACHE = new WeakMap<ScaleProps, Timing>();
const timingOf = (p: ScaleProps) => {
  let t = CACHE.get(p);
  if (!t) {
    t = makeTiming(p);
    CACHE.set(p, t);
  }
  return t;
};

export const TimingProvider: React.FC<{ props: ScaleProps; children: React.ReactNode }> = ({ props, children }) =>
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
