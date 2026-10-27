// THE TWO-HALF CAT (engine; NEW for video 15). A drawn side-view cat silhouette in TWO halves joined at the waist:
//   FRONT half (C.front amber tint): chest, head with 2 ears, 2 forelegs        - at -x (the head faces LEFT)
//   BACK half  (C.back cyan tint):   rump, 1 tail, 2 hind legs                   - at +x
// COUNT: 4 legs, 1 tail, 2 ears on every frame (lessons 39 / 40: no thin line leaves the body except legs, tail, ears).
// Steel outline (C.steel, 4 px). drawn · not to scale (the root tag covers it).
//
// Each half ROLLS about its own long axis (a dashed axis line, `axes` 0..1) by its own angle (pose.front / pose.back, deg:
// 0 = upside down, legs up; 180 = feet down). A roll about the long axis does not change the body's side silhouette: what
// turns is WHERE the belly and the legs are - the legs leave the body on the belly side (direction (0, -cos r) in the picture,
// foreshortened by |cos r|, drawn in front of the body when sin r > 0, behind it when < 0), the ears and the tail on the back
// side, and a lighter belly band slides across the body. So a half at 90 deg shows its legs pointing at the camera (short, with
// paw pads) - never a vanishing body. Legs: `frontTuck` / `backTuck` 0 = out (straight, long), 1 = tucked (folded at the knee
// against the body). `bend` = the V at the waist (both ends rise), `arch` = the landing arch (the spine rises), `flex` = the
// landing squash (legs shorten, the body lowers by the same amount, so the paws stay ON the floor line).
//
// The pose comes from props.cat (build_props.py: the angle curves conserve spin by construction). Mount <CatLive/> in every
// scene that shows the cat (it reads T.cat(frame)); <Cat pose/> is the pure drawing (inside your own <svg>). Never re-author
// the pose in a scene: request a curve change (BUILD.md §7). Pure components except <CatLive> (its hooks are at the top).
// CAT geometry is asserted by build_props.py (halfH, legOut): keep them equal.

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, L, rgba } from "../theme";
import { useT } from "../time";
import type { CatPose } from "../types";

export const CAT = { halfLen: 118, halfH: 34, legOut: 84, legTuck: 42, headR: 34, tailLen: 110, stroke: 4 } as const;

const rad = (d: number) => (d * Math.PI) / 180;

type Leg = { ax: number; tuck: number; side: "near" | "far" };

/** one half's drawing in its own local frame (waist at 0,0; the half extends along dir * x) */
const Half: React.FC<{ which: "front" | "back"; roll: number; tuck: number; flex: number; ghost: number; axes: number }> = ({ which, roll, tuck, flex, ghost, axes }) => {
  const dir = which === "front" ? -1 : 1;
  const tint = which === "front" ? C.front : C.back;
  const h = CAT.halfH;
  const len = CAT.halfLen;
  const by = -Math.cos(rad(roll)); // belly direction in the picture: -1 = up (upside down), +1 = down (feet down)
  const bz = Math.sin(rad(roll)); // towards the camera when > 0
  const fillA = (1 - ghost) * 0.88;
  const strokeA = 1 - 0.35 * ghost;
  // body: a rounded capsule from the waist to the end, a slightly deeper chest / rump
  const x1 = dir * len;
  const body = `M 0 ${-h} L ${x1 - dir * h * 0.9} ${-h * 1.02} Q ${x1 + dir * h * 0.25} ${-h * 1.02}, ${x1 + dir * h * 0.25} 0 Q ${x1 + dir * h * 0.25} ${h * 1.02}, ${x1 - dir * h * 0.9} ${h * 1.02} L 0 ${h} Z`;
  const legs: Leg[] = [
    { ax: dir * len * 0.7, tuck, side: "near" },
    { ax: dir * len * 0.7, tuck, side: "far" },
  ];
  // a leg: from the belly surface out along the belly direction (foreshortened by |by|); tucked = folded at the knee against
  // the body (forelegs fold towards the head, hind legs towards the waist). The paw's far edge sits exactly halfH + legOut
  // from the waist line when the half is feet down with the legs out (build_props.py's landing contact).
  const legPath = (lg: Leg) => {
    const out = CAT.legOut * (1 - 0.25 * flex) - 7.5;
    const fore = Math.max(0.18, Math.abs(by));
    const fold = which === "front" ? dir : -dir;
    const sx = lg.ax + (lg.side === "far" ? -dir * 12 : 0);
    const sy = by * (h - 7.5);
    const t = lg.tuck;
    const kxO = sx, kyO = sy + by * out * 0.55 * fore;
    const pxO = sx + (lg.side === "far" ? -dir * 4 : 0), pyO = sy + by * out * fore;
    const kxT = sx + fold * 8, kyT = sy + by * 30 * fore;
    const pxT = sx + fold * 34, pyT = sy + by * 12 * fore;
    const kx = kxO + (kxT - kxO) * t, ky = kyO + (kyT - kyO) * t;
    const px = pxO + (pxT - pxO) * t, py = pyO + (pyT - pyO) * t;
    return { d: `M ${sx} ${sy} Q ${kx} ${ky}, ${px} ${py}`, px, py, fore };
  };
  const nearInFront = bz >= 0;
  const legEls = (side: "near" | "far") =>
    legs
      .filter((l) => l.side === side)
      .map((lg, i) => {
        const p = legPath(lg);
        const behind = side === "far" ? nearInFront : !nearInFront;
        const op = behind ? 0.55 : 1;
        return (
          <g key={`${side}${i}`} opacity={op}>
            <path d={p.d} stroke={rgba(C.steel, strokeA)} strokeWidth={15} strokeLinecap="round" fill="none" />
            <path d={p.d} stroke={rgba(tint, fillA)} strokeWidth={9} strokeLinecap="round" fill="none" />
            <circle cx={p.px} cy={p.py} r={7.5} fill={rgba(tint, fillA)} stroke={rgba(C.steel, strokeA)} strokeWidth={3} />
          </g>
        );
      });
  // which leg pair draws behind the body: the far pair when the belly faces the camera, the near pair otherwise
  const behindFirst = nearInFront ? legEls("far") : legEls("near");
  const inFront = nearInFront ? legEls("near") : legEls("far");
  // the back side (ears / tail) is opposite the belly
  const sy = -by;
  return (
    <g>
      {behindFirst}
      {which === "back" ? (
        // ONE tail: from the rump's back side, curving out and away from the belly
        <path d={`M ${x1 - dir * 6} ${sy * h * 0.5} C ${x1 + dir * 50} ${sy * (h * 0.5 + 10)}, ${x1 + dir * 70} ${sy * (h + 40)}, ${x1 + dir * 96} ${sy * (h + 62)}`}
          stroke={rgba(C.steel, strokeA)} strokeWidth={14} strokeLinecap="round" fill="none" />
      ) : null}
      {which === "back" ? (
        <path d={`M ${x1 - dir * 6} ${sy * h * 0.5} C ${x1 + dir * 50} ${sy * (h * 0.5 + 10)}, ${x1 + dir * 70} ${sy * (h + 40)}, ${x1 + dir * 96} ${sy * (h + 62)}`}
          stroke={rgba(tint, fillA)} strokeWidth={8} strokeLinecap="round" fill="none" />
      ) : null}
      <path d={body} fill={rgba(tint, fillA)} stroke={rgba(C.steel, strokeA)} strokeWidth={CAT.stroke} strokeLinejoin="round" />
      {/* the belly band: a lighter stripe on the belly side (reads the roll even when the legs are foreshortened) */}
      <path d={`M ${dir * 8} ${by * h * 0.55} L ${x1 - dir * h * 0.6} ${by * h * 0.55}`} stroke={rgba(C.steelLit, 0.42 * (1 - ghost) * Math.abs(by))} strokeWidth={h * 0.5}
        strokeLinecap="round" />
      {which === "front" ? (
        <g>
          {/* the head: a circle at the front end + TWO ears on the back side + a muzzle on the belly side */}
          {[0, 1].map((e) => {
            const ex = x1 + dir * (CAT.headR * 0.9) + (e === 0 ? -1 : 1) * 14;
            const ey = sy * (CAT.headR * 0.62);
            return (
              <path key={e} d={`M ${ex - 13} ${ey} L ${ex} ${ey + sy * 30} L ${ex + 13} ${ey} Z`} fill={rgba(tint, fillA)} stroke={rgba(C.steel, strokeA)}
                strokeWidth={3.5} strokeLinejoin="round" opacity={e === 0 ? 1 : 0.8} />
            );
          })}
          <circle cx={x1 + dir * CAT.headR * 0.9} cy={0} r={CAT.headR} fill={rgba(tint, fillA)} stroke={rgba(C.steel, strokeA)} strokeWidth={CAT.stroke} />
          <circle cx={x1 + dir * CAT.headR * 1.55} cy={by * CAT.headR * 0.28} r={7} fill={rgba(C.steel, 0.8 * strokeA)} />
          <circle cx={x1 + dir * CAT.headR * 1.05} cy={-by * CAT.headR * 0.12} r={4.2} fill={rgba(C.shadow, 0.85 * strokeA)} />
        </g>
      ) : null}
      {inFront}
      {axes > 0 ? (
        <path d={`M ${-dir * 20} 0 L ${x1 + dir * (which === "front" ? CAT.headR * 2.1 : 40)} 0`} stroke={rgba(C.steelLit, 0.9 * axes)} strokeWidth={3}
          strokeDasharray="10 8" fill="none" />
      ) : null}
    </g>
  );
};

/** THE CAT (pure, inside your own <svg>): pose from T.cat(frame); `axes` 0..1 shows each half's dashed roll axis */
export const Cat: React.FC<{ pose: CatPose; axes?: number; opacity?: number }> = ({ pose, axes = 0, opacity = 1 }) => {
  if (pose.vis <= 0 || opacity <= 0) return null;
  const b = pose.bend / 2 - pose.arch * 7;
  const dy = CAT.legOut * 0.25 * pose.flex;
  return (
    <g opacity={pose.vis * opacity} transform={`translate(${pose.x} ${pose.y + dy}) scale(${pose.scale})`}>
      <g transform={`rotate(${b})`}>
        <Half which="front" roll={pose.front} tuck={pose.frontTuck} flex={pose.flex} ghost={pose.ghost} axes={axes} />
      </g>
      <g transform={`rotate(${-b})`}>
        <Half which="back" roll={pose.back} tuck={pose.backTuck} flex={pose.flex} ghost={pose.ghost} axes={axes} />
      </g>
      {/* the waist joint */}
      <circle cx={0} cy={0} r={9} fill={C.drapeDeep} stroke={rgba(C.steel, 1 - 0.35 * pose.ghost)} strokeWidth={3} />
    </g>
  );
};

/** THE CAT, live: a full-frame svg drawing T.cat(frame). Mount it in EVERY scene of yours that shows the cat. */
export const CatLive: React.FC<{ axes?: number; opacity?: number }> = ({ axes = 0, opacity = 1 }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const pose = T.cat(frame);
  if (pose.vis <= 0) return null;
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
      <Cat pose={pose} axes={axes} opacity={opacity} />
    </svg>
  );
};
