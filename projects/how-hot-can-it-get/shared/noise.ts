// Deterministic noise (copied from projects/what-if-earth-stopped-spinning/shared/noise.ts, video 12 (itself video 11)). Everything that wobbles, flickers or scatters goes through these (seeded by string +
// index) as a function of the frame. Never Math.random / Date.now.

import { random } from "remotion";

/** Uniform 0..1 for a (seed, index) pair. */
export const rnd = (seed: string, i: number | string = 0) => random(`${seed}:${i}`);

/** Smooth 1-D value noise in -1..1 (cosine-interpolated lattice). */
export const noise1 = (seed: string, t: number) => {
  const i = Math.floor(t);
  const f = t - i;
  const a = rnd(seed, i) * 2 - 1;
  const b = rnd(seed, i + 1) * 2 - 1;
  const s = (1 - Math.cos(f * Math.PI)) / 2;
  return a + (b - a) * s;
};

/** Irregular two-octave flicker in [lo, hi]. */
export const flicker = (seed: string, frame: number, lo = 0.78, hi = 1.0) => {
  const n = 0.65 * noise1(seed, frame / 3.2) + 0.35 * noise1(`${seed}b`, frame / 1.3);
  return lo + (hi - lo) * (0.5 + 0.5 * Math.max(-1, Math.min(1, n)));
};

/**
 * A drift exactly periodic over `period` frames (pass T.loopPeriod), so the last frame equals the first: ambient drifts MUST use this as loopDrift(T.loopFrame(frame), T.loopPeriod), so the loop-hold frames compose
 * exactly like frame 0. Returns -1..1.
 */
export const loopDrift = (frame: number, period: number, cycles = 1, phase = 0) =>
  Math.sin((2 * Math.PI * cycles * frame) / period + phase);

/** A seeded 2-D jitter vector of length in [lo, hi] px, new every 2 frames (pass T.loopFrame(frame)). */
export const jitterOnTwos = (seed: string, frame: number, lo: number, hi: number) => {
  const s = Math.floor(frame / 2);
  const m = lo + (hi - lo) * rnd(seed, `m${s}`);
  const a = 2 * Math.PI * rnd(seed, `a${s}`);
  return { x: m * Math.cos(a), y: m * Math.sin(a) };
};

/** CSS-safe id from React's useId() (call useId() UNCONDITIONALLY at the top of the component: lesson 1). */
export const cssId = (raw: string, prefix = "i") => `${prefix}${raw.replace(/[^a-zA-Z0-9_-]/g, "")}`;
