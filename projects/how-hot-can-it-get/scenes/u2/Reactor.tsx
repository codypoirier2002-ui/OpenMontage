// sc06 · Reactor · U2 (BUILD.md §3 / §7). The ROOT draws the window reopening on K2 (583-591, 'AI illustration'), the rail
// re-scale (583-607) and the KSTAR tick (SEATED kstarSeat 652, X7). THIS scene draws:
//   - the KSTAR hero label '100,000,000 °C' + 'KSTAR · Korea · 48 s · 2024' (the rung's own verified strings) on a
//     smoked-glass plate inside the window's top-left, level with the KSTAR tick (T.railY), joined to it by a short
//     leader; the number in the glow's computed black-body colour (= bbRgb(100 million K)); the whole plate FALLS onto
//     its seat with T.seat (gravity ease-in, still moving on 651, down ON 652);
//   - a thin 48-second timer arc: a dial on the plate whose arc draws clockwise from 'forty-eight' (T.sfx.timerArc 710)
//     to the end of 'seconds.' (no SFX: a continuous draw, no landing);
//   - everything out by 770 (the K2 -> S4 crossfade is root).
// Hooks at the top, before any early return (lesson 1). No blend modes (lesson 24).
import React from "react";
import { useCurrentFrame } from "remotion";
import { lighten } from "../../shared/blackbody";
import { C, FONT, glass, L, rgba } from "../../theme";
import { prog, useT } from "../../time";
import type { Mount, SceneProps } from "../../types";
import { HALO, Odometer } from "./common";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const PLATE_X = L.window.x0 + 24;
const NUM_PX = 76;
const DESC_PX = 28;
const DIAL_R = 46; // QA B12: big enough to read as a timer at phone size
const DIAL_SW = 8;

const rgbCss = (c: [number, number, number], a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

export const Reactor: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  const rung = T.rung("kstar");
  const s = T.seat(frame, T.sfx.kstarSeat, 8, 18);
  if (!s.visible) return null;
  const g = T.glow(frame);
  const rungY = T.railY(rung.L, frame);
  const outA = 1 - prog(frame, to - 11, to - 1);
  const a = s.opacity * outA;
  // the timer: dial in from timerArc - 6 (fully there ON timerArc), arc 0 -> 1 from timerArc to the end of 'seconds.'
  const arcFrom = T.sfx.timerArc;
  const arcTo = T.end("s3", "seconds");
  const dialA = prog(frame, arcFrom - 6, arcFrom);
  const p = prog(frame, arcFrom, arcTo);
  const circ = 2 * Math.PI * DIAL_R;
  const ang = -Math.PI / 2 + p * 2 * Math.PI;
  const box = DIAL_R * 2 + DIAL_SW * 2 + 4;
  const cx = box / 2;
  const arcCol = rgbCss(lighten(g.rgb, 0.3));
  const plateTop = rungY - 4 + s.y;
  return (
    <>
      {/* leader: tick end (x 204) -> plate edge, level with the KSTAR tick */}
      <div style={{ position: "absolute", left: L.rail.tickX1 + 2, top: rungY - 1 + s.y, width: PLATE_X - L.rail.tickX1 - 2, height: 2,
        backgroundColor: g.css(0.9), opacity: a }} />
      <div style={{ position: "absolute", left: PLATE_X, top: plateTop, opacity: a, padding: "10px 20px 12px 18px", borderRadius: 12,
        border: `1.5px solid ${rgba(C.ironLit, 0.95)}`, ...glass(0.7) }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{ lineHeight: 1 }}>
            <Odometer text={rung.num} size={NUM_PX} color={g.css(1)} />
          </div>
          <svg width={box} height={box} viewBox={`0 0 ${box} ${box}`} style={{ opacity: dialA, flex: "none" }}>
            <circle cx={cx} cy={cx} r={DIAL_R} stroke={rgba(C.ironLit, 0.9)} strokeWidth={3} fill="none" />
            <line x1={cx} y1={cx - DIAL_R - 7} x2={cx} y2={cx - DIAL_R + 7} stroke={C.bone} strokeWidth={3} opacity={0.85} />
            {p > 0 ? (
              <circle cx={cx} cy={cx} r={DIAL_R} stroke={arcCol} strokeWidth={DIAL_SW} fill="none" strokeDasharray={`${circ} ${circ}`}
                strokeDashoffset={circ * (1 - p)} transform={`rotate(-90 ${cx} ${cx})`} />
            ) : null}
            <line x1={cx} y1={cx} x2={cx + Math.cos(ang) * (DIAL_R - 13)} y2={cx + Math.sin(ang) * (DIAL_R - 13)} stroke={C.bone} strokeWidth={4} strokeLinecap="round" />
            <circle cx={cx} cy={cx} r={5.5} fill={C.bone} />
          </svg>
        </div>
        <div style={{ fontFamily: FONT.mono, fontWeight: 400, fontSize: DESC_PX, lineHeight: 1.2, color: C.bone, whiteSpace: "nowrap", marginTop: 4, textShadow: HALO }}>
          {rung.label}
        </div>
      </div>
    </>
  );
};
