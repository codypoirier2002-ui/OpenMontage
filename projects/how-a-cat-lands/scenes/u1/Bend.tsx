// sc05 · Bend (U1). 'Then it bends in the middle, so each half can turn on its own.'
// U1: <CatLive/> - the curves bend the waist into a V from bendStart (X5 creak on that first moving frame) to bendSeat. A
// steel hinge ring pulses out of the waist joint from bendStart (first moving frame) and is gone by 'so'. On 'so each half'
// each half's dashed roll AXIS fades in (fully on by dialsIn, then on through sc06 to the 650 / 651 seam), and each half is
// named under its own body in its own colour ('FRONT' amber under the front half, 'BACK' cyan under the back half: the
// colour rule allows each half's own name), with the dials (<DialsLive/>: in on dialsIn, 'total spin: 0' on totalSeat,
// both from the curves). The names leave before the scene ends (the TUCK pulse at 542 starts the next claim; the dials keep
// their own 'FRONT' / 'BACK'). '02 BEND' ticks ON tick02 (root). Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { CatLive, CAT } from "../../shared/Cat";
import { DialsLive } from "../../shared/Dials";
import { C, E, FONT, L, rgba } from "../../theme";
import { prog, useT } from "../../time";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const NAME_DY = 74; // px below each half's axis midpoint (the back side: no legs there while upside down)

export const Bend: React.FC<SceneProps> = ({ to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const pose = T.cat(frame);
  const soFrame = T.at("s2", "so");
  const axes = prog(frame, soFrame, T.sfx.dialsIn, E.calm);
  // the hinge ring: first visible ON bendStart (the creak), expanding and fading out by 'so'
  const hk = prog(frame, T.sfx.bendStart - 1, soFrame - 6);
  const hinge = frame >= T.sfx.bendStart && hk < 1 ? hk : -1;
  // the names: in with the axes, out before the scene ends
  const names = prog(frame, soFrame, T.sfx.dialsIn, E.calm) * (1 - prog(frame, to - 10, to - 2, E.calm));
  const b = ((pose.bend / 2 - pose.arch * 7) * Math.PI) / 180;
  const mid = CAT.halfLen * 0.72 * pose.scale;
  const front = { x: pose.x - mid * Math.cos(b), y: pose.y - mid * Math.sin(b) + NAME_DY };
  const back = { x: pose.x + mid * Math.cos(b), y: pose.y - mid * Math.sin(b) + NAME_DY };
  const name = (p: { x: number; y: number }, text: string, color: string) => (
    <div style={{ position: "absolute", left: p.x, top: p.y, transform: "translate(-50%, -50%)", fontFamily: FONT.display, fontWeight: 700, fontSize: 30,
      letterSpacing: 2, color, opacity: names, whiteSpace: "nowrap", textShadow: "0 2px 8px rgba(28,43,42,0.6)" }}>
      {text}
    </div>
  );
  return (
    <>
      <CatLive axes={axes} />
      {hinge >= 0 ? (
        <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
          {[0, 0.35].map((d, i) => {
            const k = Math.max(0, Math.min(1, hinge - d) / (1 - d));
            if (k <= 0 || k >= 1) return null;
            return <circle key={i} cx={pose.x} cy={pose.y} r={14 + 46 * k} fill="none" stroke={rgba(C.steelLit, 0.9 * (1 - k))} strokeWidth={4} />;
          })}
        </svg>
      ) : null}
      {names > 0 ? (
        <>
          {name(front, T.labels.front, C.front)}
          {name(back, T.labels.back, C.back)}
        </>
      ) : null}
      <DialsLive />
    </>
  );
};
