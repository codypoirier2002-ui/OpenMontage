// sc04 · FindUp (U1). 'First, its inner ear finds which way is up.'
// ROOT: the window has closed (catReset); the ELAPSED clock starts ON clockStart; '01 FIND UP' ticks ON tick01 (X4).
// U1: <CatLive/> (the curves reset the cat upside down at the top, fading in; head LEFT, ears DOWN, legs UP). Under it, a
// drawn INSET panel (its own 'drawn · not to scale' SceneTag, in the Overlay, from the panel's first visible frame): the
// inner ear (three semicircular canals) that GLOWS from innerEar ('inner'), tied to the cat's head by a dashed steel ring
// (wide enough to clear both ears: lessons 39/40) and a leader; beside it a compass NEEDLE that starts pointing along the
// cat's own back (down: the cat is upside down) and swings round to the ceiling with a gravity ease-in from 'which', still
// moving on tick01 - 1 and fully UP ON tick01 ('up.', the X4 tick), where 'UP' seats at its tip. The label 'inner ear:
// which way is up' shares the panel's first frame. All out by the scene end (the BEND pulse at 391 is the next claim).
// Steel / bone / slate only. Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { CatLive, CAT } from "../../shared/Cat";
import { Arrow, InnerEarIcon } from "../../shared/Icons";
import { WindowFrame } from "../../shared/Window";
import { Label } from "../../shared/Type";
import { SceneTag } from "../../overlay/Tag";
import { C, E, FONT, L, rgba } from "../../theme";
import { prog, useT } from "../../time";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const LABEL_TEXT = "inner ear: which way is up";
const PANEL = { x0: 140, x1: 520, y0: 650, y1: 930 };
const PW = PANEL.x1 - PANEL.x0;
const PH = PANEL.y1 - PANEL.y0;
const EAR = { x: 112, y: 118, size: 140 }; // panel-local
const NEEDLE = { x: 296, y: 140, half: 70 }; // panel-local pivot + half length
const NEEDLE_FROM = 160; // deg, clockwise from up: pointing down along the cat's back
const LABEL_Y = 966;
const RING_R = 60;

/** shared timing of the inset (picture + overlay agree) */
const useInset = (to: number) => {
  const frame = useCurrentFrame();
  const T = useT();
  const first = T.sfx.innerEar - 7; // the panel's first visible frame
  const open = prog(frame, first - 1, T.sfx.innerEar - 1, E.open) * (1 - prog(frame, to - 7, to - 1, E.calm));
  return { frame, T, first, open };
};

export const FindUp: React.FC<SceneProps> = ({ to }) => {
  const { frame, T, open } = useInset(to);
  const pose = T.cat(frame);
  const glow = prog(frame, T.sfx.innerEar, T.sfx.innerEar + 8, E.calm) * (0.85 + 0.15 * Math.cos(((frame - T.sfx.innerEar) / 24) * Math.PI * 2));
  // the needle: ease-in swing (still moving on tick01 - 1), fully UP on tick01
  const swingFrom = T.at("s2", "which");
  const sw = prog(frame, swingFrom, T.sfx.tick01, E.drop);
  const ang = NEEDLE_FROM * (1 - sw);
  const up = T.seat(frame, T.sfx.tick01, 4, 10);
  const r = (ang * Math.PI) / 180;
  const nx = Math.sin(r) * NEEDLE.half;
  const ny = -Math.cos(r) * NEEDLE.half;
  // the head (pure read of the curves): centre of the head circle, bend 0 here
  const head = { x: pose.x - (CAT.halfLen + CAT.headR * 0.9) * pose.scale, y: pose.y };
  return (
    <>
      <CatLive />
      {open > 0 ? (
        <>
          <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, opacity: open * pose.vis }}>
            <circle cx={head.x} cy={head.y} r={RING_R} fill="none" stroke={rgba(C.steelLit, 0.85)} strokeWidth={3} strokeDasharray="9 7" />
            <path d={`M ${head.x} ${head.y + RING_R} L ${head.x} ${PANEL.y0 - 4}`} stroke={rgba(C.steelLit, 0.85)} strokeWidth={3} strokeDasharray="9 7" />
          </svg>
          <WindowFrame box={PANEL} open={open} radius={18} frame={5}>
            <svg width={PW} height={PH} style={{ position: "absolute", left: 0, top: 0 }}>
              <rect x={0} y={0} width={PW} height={PH} fill={C.drapeDeep} />
              <InnerEarIcon x={EAR.x} y={EAR.y} size={EAR.size} glow={glow} color={C.steelLit} />
              {/* the needle's dial ring */}
              <circle cx={NEEDLE.x} cy={NEEDLE.y} r={NEEDLE.half + 12} fill="none" stroke={rgba(C.steelEdge, 0.8)} strokeWidth={2.5} />
              <line x1={NEEDLE.x} y1={NEEDLE.y - NEEDLE.half - 18} x2={NEEDLE.x} y2={NEEDLE.y - NEEDLE.half - 6} stroke={C.steelLit} strokeWidth={4} strokeLinecap="round" />
              <path d={`M ${NEEDLE.x - nx * 0.55} ${NEEDLE.y - ny * 0.55} L ${NEEDLE.x} ${NEEDLE.y}`} stroke={rgba(C.steelEdge, 0.95)} strokeWidth={6} strokeLinecap="round" />
              <Arrow x1={NEEDLE.x} y1={NEEDLE.y} x2={NEEDLE.x + nx} y2={NEEDLE.y + ny} color={C.bone} width={7} head={22} />
              <circle cx={NEEDLE.x} cy={NEEDLE.y} r={7} fill={C.steel} />
            </svg>
            {up.visible ? (
              <div style={{ position: "absolute", left: NEEDLE.x, top: NEEDLE.y - NEEDLE.half - 44 + up.y, transform: "translate(-50%, -50%)", opacity: up.opacity,
                fontFamily: FONT.display, fontWeight: 700, fontSize: 34, letterSpacing: 2, color: C.bone, whiteSpace: "nowrap", lineHeight: 1 }}>
                {T.labels.up}
              </div>
            ) : null}
          </WindowFrame>
          <Label x={PANEL.x0} y={LABEL_Y} text={LABEL_TEXT} size={28} variant="chip" weight={500} opacity={open} />
        </>
      ) : null}
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ to }) => {
  const { T, first, open } = useInset(to);
  if (open <= 0) return null;
  return <SceneTag x={PANEL.x0 + 14} y={PANEL.y1 - 52} enter={first} exit={to - 1} text={T.labels.drawn} opacity={Math.min(1, open * 1.5)} />;
};
