// Timing helpers. EVERY trigger goes through a word, a scene window, a key frame or one of the root curves from the measured
// timeline (artifacts/timeline.json -> props). Never hard-code seconds or frame numbers in a scene. Copied from
// projects/how-a-mosquito-drinks/time.ts (video 14, QA passed; itself videos 12-13) and re-dressed for the test lab.
//
//   const T = useT();
//   T.at("s3", "front", 2)         -> onset frame of the 2nd 'front' of s3 (case/punctuation-insensitive)
//   T.end("s5", "vet")             -> frame at which 'vet.' ends (= T.sfx.vetEndFrame)
//   T.scene("sc06")                -> { from, to, dur };  T.section("s4") -> { from, to, dur }
//   T.sfx.turnStart ...            -> key frames from build_soundtrack.py (every SFX is already ON its frame)
//   THE TEST LAB (root curves; shared/Rig.tsx, Checklist.tsx, Window.tsx draw them):
//   T.rig(frame)                   -> { clamp 0..1 (open), floor 0..1, floorY, drawnTag 0..1 }
//   T.check(frame)                 -> per row: { id, text, tick, progress 0..1 (the mark draws), done }
//   T.clock(frame)                 -> { seconds, text: '0.00 s', stopped }
//   T.win(frame)                   -> the window frame's open 0..1;  T.plate(id, frame) -> the plate's alpha 0..1
//   T.tagAt(frame)                 -> the ONE window tag on screen (the plate with the larger alpha: hard swap, lesson 38)
//   T.strip(frame)                 -> the Marey strip's cell position (float; integer = a cell at rest at the window top)
//   THE CAT (units mount <CatLive/> / <DialsLive/> from shared/): the SAME curves in every scene, so seams match
//   T.cat(frame)                   -> CatPose (types.ts)
//   T.dials(frame)                 -> { front, back, total } visibilities 0..1 (the needles read T.cat(frame).front / .back)
//   T.seat(frame, seatFrame, n, drop) -> { k, y, opacity, seated, visible }: an element that FALLS (gravity ease-in, still
//                                     moving >= 1 px on seat - 1) and is FULLY SEATED on its seat frame (lessons 4, 22)
//   T.driftFrame(frame)            -> the frame ambient drift should use (no freezes planned: identity)
//   T.loopFrame(frame), T.loopPeriod -> every ambient clock is PERIODIC over loopPeriod (= the release of 'vet.') and reads
//                                     frame 0 from it, so the settle is still. Grain / drift seed =
//                                     T.driftFrame(T.loopFrame(frame)) (loopFrame FIRST, lesson 11).

import React, { createContext, useContext } from "react";
import type { CatPose, CatProps, MediaId, RowId, SceneId, SectionId, WindowPlate, Word } from "./types";

const norm = (t: string) => t.toLowerCase().replace(/[^a-z0-9]/g, "");

export type Span = { from: number; to: number; dur: number };
export type RowState = { id: RowId; text: string; tick: number; progress: number; done: boolean };

export type Timing = {
  total: number;
  fps: number;
  lead: number;
  word: (section: SectionId, text: string, nth?: number) => Word;
  at: (section: SectionId, text: string, nth?: number) => number;
  end: (section: SectionId, text: string, nth?: number) => number;
  scene: (id: SceneId) => Span;
  section: (id: SectionId) => Span;
  sfx: CatProps["audio"];
  motion: CatProps["motion"];
  settle: CatProps["settle"];
  cta: CatProps["cta"];
  labels: CatProps["labels"];
  rig: (frame: number) => { clamp: number; floor: number; floorY: number; drawnTag: number };
  rigInfo: CatProps["rig"];
  check: (frame: number) => RowState[];
  checklistInfo: CatProps["checklist"];
  clock: (frame: number) => { seconds: number; text: string; stopped: boolean };
  win: (frame: number) => number;
  plate: (id: MediaId, frame: number) => number;
  tagAt: (frame: number) => string | null;
  strip: (frame: number) => number;
  windowInfo: CatProps["window"];
  media: (id: MediaId) => WindowPlate;
  cat: (frame: number) => CatPose;
  dials: (frame: number) => { front: number; back: number; total: number };
  seat: (frame: number, seatFrame: number, frames?: number, dropPx?: number) => { k: number; y: number; opacity: number; seated: boolean; visible: boolean };
  freezes: { from: number; to: number }[];
  driftFrame: (frame: number) => number;
  loopFrame: (frame: number) => number;
  loopPeriod: number;
  layers: CatProps["layers"];
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

export const makeTiming = (p: CatProps): Timing => {
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
  const CL = p.checklist;
  const check = (frame: number): RowState[] =>
    CL.rows.map((r) => {
      // ease-in (k^3) so the long stroke is still well short on tick - 1 and completes ON the tick frame (video 14 QA B5)
      const progress = clamp01((frame - (r.tick - CL.tickF)) / CL.tickF) ** 3;
      return { id: r.id, text: r.text, tick: r.tick, progress, done: frame >= r.tick };
    });
  const clock = (frame: number) => {
    const s = sample(CL.clock, Math.floor(frame));
    return { seconds: s, text: `${s.toFixed(2)} s`, stopped: frame >= CL.clockStop };
  };
  // a GRAVITY drop (ease-in, y = -drop * (1 - k^2)) so the element is still visibly moving on seat - 1 and lands ON the
  // seat frame (the SFX is there; lessons 4, 22)
  const seat = (frame: number, seatFrame: number, frames = 8, dropPx = 18) => {
    const k = clamp01((frame - (seatFrame - frames)) / frames);
    return { k, y: -dropPx * (1 - k * k), opacity: clamp01(k * 1.6), seated: frame >= seatFrame, visible: frame > seatFrame - frames };
  };
  const C_ = p.cat;
  const cat = (frame: number): CatPose => ({
    x: sample(C_.x, frame), y: sample(C_.y, frame), front: sample(C_.front, frame), back: sample(C_.back, frame),
    frontTuck: sample(C_.frontTuck, frame), backTuck: sample(C_.backTuck, frame), bend: sample(C_.bend, frame),
    arch: sample(C_.arch, frame), flex: sample(C_.flex, frame), vis: sample(C_.vis, frame), ghost: sample(C_.ghost, frame), scale: C_.scale,
  });
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
    rig: (frame) => ({ clamp: sample(p.rig.clamp, frame), floor: sample(p.rig.floor, frame), floorY: p.rig.floorY, drawnTag: sample(p.rig.drawnTag, frame) }),
    rigInfo: p.rig,
    check,
    checklistInfo: CL,
    clock,
    win: (frame) => sample(p.window.open, frame),
    plate: (id, frame) => sample(plates[id].alpha, frame),
    tagAt,
    strip: (frame) => sample(plates.A1.step ?? [0], frame),
    windowInfo: p.window,
    media: (id) => plates[id],
    cat,
    dials: (frame) => ({ front: sample(p.dials.front, frame), back: sample(p.dials.back, frame), total: sample(p.dials.total, frame) }),
    seat,
    freezes,
    driftFrame,
    loopFrame,
    loopPeriod,
    layers: p.layers,
  };
};

const TimingCtx = createContext<Timing | null>(null);
const CACHE = new WeakMap<CatProps, Timing>();
const timingOf = (p: CatProps) => {
  let t = CACHE.get(p);
  if (!t) {
    t = makeTiming(p);
    CACHE.set(p, t);
  }
  return t;
};

export const TimingProvider: React.FC<{ props: CatProps; children: React.ReactNode }> = ({ props, children }) =>
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
