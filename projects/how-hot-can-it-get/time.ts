// Timing helpers. EVERY trigger goes through a word, a scene window, a key frame or one of the root schedules from the
// measured timeline (artifacts/timeline.json -> props). Never hard-code seconds or frame numbers in a scene. Pattern
// copied from projects/what-if-earth-stopped-spinning/time.ts (video 12, delivered, QA passed).
//
//   const T = useT();
//   T.at("s2", "fifty-seven")    -> onset frame of 'fifty-seven' (case/punctuation-insensitive; nth for repeats:
//                                   T.at("s3", "million", 2) = the second 'million')
//   T.end("s5", "know")          -> frame at which 'know.' ends (= T.sfx.knowEndFrame)
//   T.scene("sc08")              -> { from, to, dur };  T.section("s4") -> { from, to, dur }
//   T.sfx.dvSeat ...             -> key frames from build_soundtrack.py (seats, landings, the sweep, the chord, the CTA) -
//                                   every SFX is already ON its frame
//   THE BLACK-BODY WORLD (root schedules; shared/GlowField.tsx, shared/Ladder.tsx, shared/Window.tsx draw them):
//   T.glow(frame)                -> { k, i, rgb, lum, css(alpha) }: the frame's glow temperature (K), intensity, colour (css at
//                                   its display luminance: dim dull red at the Draper point)
//   T.rail(frame)                -> { lo, ppd, camY, floor, spine, fray, q, qAlpha, cursor, chip, compactVis }
//   T.railY(L, frame)            -> screen y of log10(kelvin) = L on the ladder rail (incl. the camera)
//   T.railYK(kelvin, frame)      -> the same for a temperature in kelvin;  T.floorY(frame) -> the floor line's y
//   T.rung(id) / T.mark(id)      -> the rung / mark (kelvin, L, strings, seat / at)
//   T.zeros(frame)               -> { value, alpha, L }: the zeros counter chip
//   T.win(frame)                 -> { open, dim, lut }: the root WINDOW;  T.media(id) -> its plate schedule
//   T.seat(frame, seatFrame, n, drop) -> { k, y, opacity, seated, visible }: an element that FALLS (gravity ease-in, still
//                                   moving >= 1 px on seat - 1) and is FULLY SEATED on its seat frame (lessons 4, 22)
//   T.driftFrame(frame)          -> the frame ambient drift should use (no freezes planned: identity)
//   T.loopFrame(frame), T.loopPeriod -> every ambient clock is PERIODIC over loopPeriod (= the release of 'know.') and
//                                   reads frame 0 from it, so the settle is still. Grain / drift seed =
//                                   T.driftFrame(T.loopFrame(frame)) (loopFrame FIRST, lesson 11).

import React, { createContext, useContext } from "react";
import { bbRgb, glowLum } from "./shared/blackbody";
import type { HotProps, Mark, MarkId, MediaId, Rung, RungId, SceneId, SectionId, WindowMedia, Word } from "./types";

const norm = (t: string) => t.toLowerCase().replace(/[^a-z0-9]/g, "");

export type Span = { from: number; to: number; dur: number };
export type GlowState = { k: number; i: number; rgb: [number, number, number]; lum: number; css: (alpha?: number) => string };
export type RailState = {
  lo: number; ppd: number; camY: number; floor: number; spine: number; fray: number; q: number; qAlpha: number; cursor: number; chip: number; compactVis: number;
};
const RAIL_KEYS = ["lo", "ppd", "camY", "floor", "spine", "fray", "q", "qAlpha", "cursor", "chip", "compactVis"] as const;

export type Timing = {
  total: number;
  fps: number;
  lead: number;
  word: (section: SectionId, text: string, nth?: number) => Word;
  at: (section: SectionId, text: string, nth?: number) => number;
  end: (section: SectionId, text: string, nth?: number) => number;
  scene: (id: SceneId) => Span;
  section: (id: SectionId) => Span;
  sfx: HotProps["audio"];
  settle: HotProps["settle"];
  cta: HotProps["cta"];
  labels: HotProps["labels"];
  glow: (frame: number) => GlowState;
  glowInfo: HotProps["glow"];
  rail: (frame: number) => RailState;
  railY: (L: number, frame: number) => number;
  railYK: (kelvin: number, frame: number) => number;
  floorY: (frame: number) => number;
  railInfo: HotProps["rail"];
  rungs: Rung[];
  rung: (id: RungId) => Rung;
  marks: Mark[];
  mark: (id: MarkId) => Mark;
  zeros: (frame: number) => { value: number; alpha: number; L: number };
  win: (frame: number) => { open: number; dim: number; lut: number };
  windowInfo: HotProps["window"];
  media: (id: MediaId) => WindowMedia;
  seat: (frame: number, seatFrame: number, frames?: number, dropPx?: number) => { k: number; y: number; opacity: number; seated: boolean; visible: boolean };
  freezes: { from: number; to: number }[];
  driftFrame: (frame: number) => number;
  loopFrame: (frame: number) => number;
  loopPeriod: number;
  layers: HotProps["layers"];
};

const clamp01 = (x: number) => Math.min(1, Math.max(0, x));

export const makeTiming = (p: HotProps): Timing => {
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

  // per-frame channels, linearly interpolated between frames (fractional frames are allowed)
  const sample = (arr: number[], frame: number) => {
    const f = Math.max(0, Math.min(total - 1, frame));
    const i = Math.floor(f);
    const j = Math.min(total - 1, i + 1);
    const x = f - i;
    return x > 0 ? arr[i] + (arr[j] - arr[i]) * x : arr[i];
  };
  const G = p.glow;
  // the temperature is interpolated in LOG space between frames (the sweep is a log roll)
  const logK = G.k.map(Math.log10);
  const glowAt = (frame: number): GlowState => {
    const k = Math.pow(10, sample(logK, frame));
    const rgb = bbRgb(k);
    // css() = the colour at its display luminance (dim dull red at the Draper point -> full by ~1,500 K; QA B9); rgb = hue only
    const lum = glowLum(k);
    const c = rgb.map((v) => Math.round(v * lum));
    return { k, i: sample(G.i, frame), rgb, lum, css: (alpha = 1) => `rgba(${c[0]},${c[1]},${c[2]},${alpha})` };
  };
  const R = p.rail;
  const rail = (frame: number): RailState => {
    const out = {} as RailState;
    for (const k of RAIL_KEYS) out[k] = sample(R[k], frame);
    return out;
  };
  const railY = (Lv: number, frame: number) => {
    const r = rail(frame);
    return R.axisY0 + r.camY - (Lv - r.lo) * r.ppd;
  };
  const rungs = Object.fromEntries(p.rungs.map((r) => [r.id, r])) as Record<RungId, Rung>;
  const marks = Object.fromEntries(p.marks.map((m) => [m.id, m])) as Record<MarkId, Mark>;
  const Z = p.zeros;
  const W = p.window;
  const media = Object.fromEntries(W.media.map((m) => [m.id, m])) as Record<MediaId, WindowMedia>;
  // a GRAVITY drop (ease-in, y = -drop * (1 - k^2)) so the element is still visibly moving on seat - 1 (drop 18, 8 f:
  // 4.2 px left to fall) and lands ON the seat frame (the SFX is there; lessons 4, 22)
  const seat = (frame: number, seatFrame: number, frames = 8, dropPx = 18) => {
    const k = clamp01((frame - (seatFrame - frames)) / frames);
    return { k, y: -dropPx * (1 - k * k), opacity: clamp01(k * 1.6), seated: frame >= seatFrame, visible: frame > seatFrame - frames };
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
    settle: p.settle,
    cta: p.cta,
    labels: p.labels,
    glow: glowAt,
    glowInfo: G,
    rail,
    railY,
    railYK: (kelvin, frame) => railY(Math.log10(kelvin), frame),
    floorY: (frame) => R.floorY + sample(R.camY, frame),
    railInfo: R,
    rungs: p.rungs,
    rung: (id) => rungs[id],
    marks: p.marks,
    mark: (id) => marks[id],
    zeros: (frame) => ({ value: Z.value[Math.max(0, Math.min(total - 1, Math.floor(frame)))], alpha: sample(Z.alpha, frame), L: sample(Z.L, frame) }),
    win: (frame) => ({ open: sample(W.open, frame), dim: sample(W.dim, frame), lut: sample(W.lut, frame) }),
    windowInfo: W,
    media: (id) => media[id],
    seat,
    freezes,
    driftFrame,
    loopFrame,
    loopPeriod,
    layers: p.layers,
  };
};

const TimingCtx = createContext<Timing | null>(null);
const CACHE = new WeakMap<HotProps, Timing>();
const timingOf = (p: HotProps) => {
  let t = CACHE.get(p);
  if (!t) {
    t = makeTiming(p);
    CACHE.set(p, t);
  }
  return t;
};

export const TimingProvider: React.FC<{ props: HotProps; children: React.ReactNode }> = ({ props, children }) =>
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
