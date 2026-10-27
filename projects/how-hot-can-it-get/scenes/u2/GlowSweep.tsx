// sc05 · GlowSweep · U2 · HERO 1 (BUILD.md §3 / §7). The ROOT draws the world: the window closing (481-489), the glow
// sweep (sweepStart 483 -> sunCoreSeat 552), the cursor bead, the three marks, the 'black-body colour' chip, the Sun's-core
// tick (SEATED 552, X4 crest + X7). THIS scene draws only the rolling number and its seat:
//   - the number IS the glow's temperature: T.glow(f).k - 273.15, rounded to 3 significant figures and set like the
//     verified rung strings ('~464 °C' at 483, '~525 °C' at the Draper point, ... '~15,000,000 °C' at the seat);
//   - its fill IS the glow's computed black-body colour (T.glow(f).rgb = bbRgb(k)) from the Draper point (490) on; below
//     it (464-516 °C) the number is unlit Bone (honesty: nothing below the Draper point glows);
//   - it sits ABOVE the cursor (the rail's mark labels are always at / below the cursor, so the number never crosses
//     them), raised 18 px, and FALLS onto its seat with T.seat (gravity ease-in, still moving on 551, down ON 552) while
//     "Sun's core" appears under it ON the seat (552) - never under an intermediate number (QA A-M1);
//   - out by 583 (the window reopens; the root's compact '~15,000,000 °C' takes over on the rail).
// Hooks at the top, before any early return (lesson 1). No blend modes (lesson 24).
import React from "react";
import { useCurrentFrame } from "remotion";
import { DRAPER_K } from "../../shared/blackbody";
import { C, FONT, L } from "../../theme";
import { prog, useT } from "../../time";
import type { Mount, SceneProps } from "../../types";
import { HALO, Odometer, rollText } from "./common";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

/** the number: left edge (aligned with the chip above), cap-centre line, size */
const NUM_X = L.chip.x + 2;
const NUM_Y = 322;
const NUM_PX = 100;
const DESC_PX = 34;
/** Saira Condensed 700 at line-height 1: the caps' centre sits 0.504 em below the line box top */
const CAP_MID = 0.504;

export const GlowSweep: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  const start = T.sfx.sweepStart;
  if (frame < start) return null;
  const seatF = T.sfx.sunCoreSeat;
  const rung = T.rung("suncore");
  const g = T.glow(frame);
  const s = T.seat(frame, seatF, 8, 18);
  const seated = frame >= seatF;
  const text = seated ? rung.num : rollText(g.k - 273.15);
  const lit = g.k >= DRAPER_K - 0.01;
  // QA B9: dim dull red at the Draper point, brightening with temperature (floored at 55 % so the number stays legible)
  const nl = Math.max(0.55, g.lum);
  const color = lit ? `rgb(${g.rgb.map((v) => Math.round(v * nl)).join(",")})` : C.bone;
  // QA A-m2: hidden until the Venus plate is gone (the close ends 489): never a third value over the Venus plate
  const closed = T.sfx.windowClose1 + 8;
  const inA = prog(frame, closed - 1, closed + 1);
  const outA = 1 - prog(frame, to - 12, to - 2);
  const a = inA * outA;
  const top = NUM_Y - NUM_PX * CAP_MID + s.y;
  return (
    <>
      <div style={{ position: "absolute", left: NUM_X, top, opacity: a, lineHeight: 1 }}>
        <Odometer text={text} size={NUM_PX} color={color} />
      </div>
      {seated ? (
        // QA A-M1 / B1: "Sun's core" appears ON the seat (552), never under an intermediate number
        <div style={{ position: "absolute", left: NUM_X + 4, top: NUM_Y + NUM_PX * 0.44, opacity: outA, fontFamily: FONT.mono, fontWeight: 400,
          fontSize: DESC_PX, lineHeight: 1.2, color: C.bone, whiteSpace: "nowrap", textShadow: HALO }}>
          {rung.label}
        </div>
      ) : null}
    </>
  );
};
