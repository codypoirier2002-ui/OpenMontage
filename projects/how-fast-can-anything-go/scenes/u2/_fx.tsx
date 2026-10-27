// U2 effects (sc07-sc12), built on the engine (shared/Devices.tsx) and the root curves through useT(). Nothing here moves
// the marker, draws a second marker or touches the 'c' line; nothing is red except the flash ON the 'c' line itself and
// nothing is white-cyan except the beam's splash. Every trigger is a key frame / a root curve; every element tied to one
// claim is gone >= 8 f before the next claim's tab page (lessons 31 / 42 / 47); nothing changes after the release of 'way.'.
//   <FallArrow/>   sc07 OVERLAY: an SVG <Arrow> on the S3 plate pointing at the Sun (the top of the plate), drawing on from
//                  fallArrow (its first frame IS fallArrow, with its label), + the label 'falling toward the Sun' (own tag box,
//                  right-aligned inside the window so the text ends at x 912); both fade out 6 f ending ON windowClose2
//                  (10 f before the LIGHT page at 875).
//   <BeamIgnite/>  sc08: the beam's head at the rail's foot ON beamStart (X5), where the beam curve's progress is still 0 and
//                  the engine draws nothing yet: the beam's first visible frame = its sound's frame (lesson 4).
//   <WallFlash/>   sc08: ON lightSeat the beam's splash (a white-cyan ring at the beam's head, 12 f: the beam's own colour)
//                  + a pulse ON the red 'c' line (the same line, brighter and wider for 14 f: red only on the line).
//   <CreepTrail/>  sc09-sc10: a stroboscopic trail on the spine: every TRAIL_STEP f from wallStart a short steel tick is left
//                  at the marker's position, fading over TRAIL_LIFE f, never within 10 px of the marker (the root draws the
//                  marker above nothing of ours: we draw over it, so we keep off it). The spacing shrinks as the marker slows:
//                  the wall. Alpha x T.mass(f): in with 'nothing' (958), GONE 1197 (< the LHC page 1205, with the mass label).
//   <StepMarks/>   sc10: 'each step': a steel mark right of the ENERGY NEEDED bar at the bar's height ON each X3 bar tick
//                  (the bar's own step frames); the gaps between the marks grow: each step costs more. Alpha = the energy
//                  alpha (gone 1197). The 'end' tick's mark is off the top with the bar.
//   <StopPulse/>   sc11: ON creepEnd / gapBracket (X6 tink) a small steel ring (r 9 -> 13: it stays under 'c') + a stop dash
//                  right of the marker, 16 f; over by 1315 (< 1358, long before 1432).
// Hooks at the top of every component, before any early return (lesson 1). No blend modes (lesson 24).

import React from "react";
import { useCurrentFrame } from "remotion";
import { tagBox } from "../../overlay/Tag";
import { Arrow } from "../../shared/Icons";
import { measure } from "../../shared/Type";
import { C, E, L, rgba } from "../../theme";
import { prog, useT } from "../../time";

const R = L.rail;

/** the verified string (scene_plan.metadata.verified_on_screen_strings; = T.labels.falling) */
export const FALLING_TEXT = "falling toward the Sun";

const TAG_PX = 24;
const TAG_PAD = 8;
const ARROW_X = L.win.x0 + 120; // left of the plate's centre: the probe sits mid-plate, the Sun fills the top (S3's prompt)
const ARROW_Y0 = L.win.y1 - 118; // the tail (the probe)
const ARROW_Y1 = L.win.y0 + 125; // the head (toward the Sun), under the label row
const ARROW_DRAW_F = 10;
const OUT_F = 6;

export const FallArrow: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const from = T.sfx.fallArrow;
  const exit = T.sfx.windowClose2;
  if (frame < from || frame >= exit) return null;
  const k = prog(frame, from, from + ARROW_DRAW_F, E.open);
  const out = 1 - prog(frame, exit - OUT_F, exit);
  const headY = ARROW_Y0 - 44 - (ARROW_Y0 - 44 - ARROW_Y1) * k; // 44 px long on its first frame, full by from + 10
  const w = measure(FALLING_TEXT, "mono", TAG_PX);
  const boxW = w + 2 * TAG_PAD;
  return (
    <>
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, opacity: out }}>
        <circle cx={ARROW_X} cy={ARROW_Y0} r={6} fill={C.bone} opacity={0.95} />
        <circle cx={ARROW_X} cy={ARROW_Y0} r={11} fill="none" stroke={C.bone} strokeWidth={1.5} opacity={0.55} />
        <Arrow x1={ARROW_X} y1={ARROW_Y0 - 14} x2={ARROW_X} y2={headY} width={4} head={14} />
      </svg>
      {/* the label: text ends at x 912 (the box flush with the window's right edge) */}
      <div style={{ ...tagBox(TAG_PX, "plain"), padding: `0 ${TAG_PAD}px`, width: boxW, left: L.win.x1 - boxW, top: L.win.y0 + 16, opacity: out }}>
        {FALLING_TEXT}
      </div>
    </>
  );
};

/** the beam's head at the rail's foot on the frames where the beam is lit (alpha > 0) but its progress is still 0: the X5
 *  shimmer starts ON beamStart and the engine draws nothing until progress > 0 (the curve's first non-zero is a frame later),
 *  so the beam's first VISIBLE frame is its sound's frame (lesson 4). The same look as the engine's head (white-cyan). */
export const BeamIgnite: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const bm = T.beam(frame);
  if (bm.alpha <= 0 || bm.progress > 0) return null;
  const headR = 7;
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, opacity: bm.alpha }}>
      <circle cx={R.x} cy={R.axisY0} r={headR * 2.6} fill={C.marker} opacity={0.2} />
      <circle cx={R.x} cy={R.axisY0} r={headR} fill="#FFFFFF" opacity={0.95} />
    </svg>
  );
};

const SPLASH_F = 12;
const LINE_FLASH_F = 14;

export const WallFlash: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const on = T.sfx.lightSeat;
  if (frame < on || frame >= on + LINE_FLASH_F) return null;
  const ks = prog(frame, on, on + SPLASH_F, E.open);
  const kl = prog(frame, on, on + LINE_FLASH_F);
  const x0 = R.tickX0 - 14;
  const x1 = R.tickX1 + 14;
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
      {/* the pulse ON the 'c' line (red only here, on the line) */}
      <line x1={x0} y1={R.cY} x2={x1} y2={R.cY} stroke={C.wall} strokeWidth={22} strokeLinecap="round" opacity={0.3 * (1 - kl)} />
      <line x1={x0} y1={R.cY} x2={x1} y2={R.cY} stroke={C.wall} strokeWidth={9 - 6 * kl} strokeLinecap="round" opacity={0.95 * (1 - kl)} />
      {/* the beam's splash at its head (the beam's own white-cyan) */}
      {ks < 1 ? <circle cx={R.x} cy={R.cY} r={8 + 22 * ks} fill="none" stroke={C.marker} strokeWidth={3 - 2 * ks} opacity={0.85 * (1 - ks)} /> : null}
      {ks < 1 ? <circle cx={R.x} cy={R.cY} r={4 + 6 * ks} fill="#FFFFFF" opacity={0.9 * (1 - ks)} /> : null}
    </svg>
  );
};

const TRAIL_STEP = 4;
const TRAIL_LIFE = 36;
const TRAIL_KEEP_OFF = 10; // px: no tick this close to the marker (we draw above it)

export const CreepTrail: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const a = T.mass(frame);
  const start = T.sfx.wallStart;
  if (a <= 0 || frame < start) return null;
  const now = T.ladder(frame);
  const ticks: React.ReactNode[] = [];
  const last = Math.min(frame, T.sfx.creepEnd);
  for (let s = start; s <= last; s += TRAIL_STEP) {
    const age = frame - s;
    if (age >= TRAIL_LIFE) continue;
    const y = T.ladder(s).y;
    if (y - now.y < TRAIL_KEEP_OFF) continue;
    const op = 0.75 * (1 - age / TRAIL_LIFE);
    ticks.push(<line key={s} x1={R.x - 10} y1={y} x2={R.x + 10} y2={y} stroke={C.steel} strokeWidth={2.5} strokeLinecap="round" opacity={op} />);
  }
  if (ticks.length === 0) return null;
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, opacity: a }}>
      {ticks}
    </svg>
  );
};

export const StepMarks: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const en = T.energy(frame);
  if (en.alpha <= 0) return null;
  const g = L.energy;
  const marks: React.ReactNode[] = [];
  for (const t of T.sfx.barTicks) {
    if (frame < t) break;
    const h = T.energy(t).barH;
    if (h < 2) continue; // the first tick is the bar's foot: the engine's baseline is already there
    const y = g.y0 - h;
    if (y < 0) continue; // 'end': off the top with the bar
    marks.push(
      <g key={t} stroke={C.steel} strokeWidth={2} strokeLinecap="round">
        <line x1={g.barX1 + 6} y1={y} x2={g.barX1 + 22} y2={y} />
        <line x1={g.barX1 + 22} y1={y} x2={g.barX1 + 22} y2={y + 7} opacity={0.6} />
      </g>,
    );
  }
  if (marks.length === 0) return null;
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, opacity: en.alpha * 0.9 }}>
      {marks}
    </svg>
  );
};

const STOP_F = 16;

export const StopPulse: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const on = T.sfx.gapBracket;
  if (frame < on || frame >= on + STOP_F) return null;
  const k = prog(frame, on, on + STOP_F, E.open);
  const ld = T.ladder(frame);
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
      {/* r 8 -> 11 (+ 1 px stroke): the ring's top stays >= 2 px under the 'c' line (the marker sits 14 px under it) */}
      <circle cx={R.x} cy={ld.y} r={8 + 3 * k} fill="none" stroke={C.steel} strokeWidth={2.5} opacity={0.9 * (1 - k)} />
      {/* the stop dash: x 262 -> 277, left of the LIGHT chip (labelX 280), shrinking back toward the rail */}
      <line x1={R.rungX1 - 6} y1={ld.y} x2={R.labelX - 3 - 8 * k} y2={ld.y} stroke={rgba(C.steel, 0.9)} strokeWidth={2} strokeLinecap="round" opacity={1 - k} />
    </svg>
  );
};
