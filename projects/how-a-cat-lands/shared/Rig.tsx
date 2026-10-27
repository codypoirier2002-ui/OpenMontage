// THE RIG (ROOT ONLY: Composition.tsx mounts <RigView/> once, above the drape, under the scenes): the steel test rail across
// the field top with the RELEASE CLAMP hanging from it (two jaws that swing open, T.rig(f).clamp 0..1, fully open ON
// T.sfx.clampOpen = the X1 click), the FLOOR LINE (a steel line + a soft shadow band, T.rig(f).floor 0..1 at L.field.floorY,
// sc09-sc10), and the header 'PROCEDURE: LANDING' (Roboto Mono 500, from frame 0: lesson 34, never an empty opening).
// Constant in the settle (the rail + clamp + header stay; the floor has gone in sc10). Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { useT } from "../time";

export const ClampJaws: React.FC<{ x: number; y0: number; y1: number; open: number }> = ({ x, y0, y1, open }) => {
  const a = 34 * open;
  const len = y1 - y0;
  return (
    <g>
      <rect x={x - 26} y={y0 - 14} width={52} height={26} rx={6} fill={C.steel} stroke={C.steelEdge} strokeWidth={3} />
      {[-1, 1].map((s) => (
        <g key={s} transform={`rotate(${s * a} ${x + s * 12} ${y0 + 10})`}>
          <path d={`M ${x + s * 12} ${y0 + 8} L ${x + s * 16} ${y0 + len - 14} Q ${x + s * 16} ${y0 + len}, ${x + s * 4} ${y0 + len}`} stroke={C.steel} strokeWidth={9}
            strokeLinecap="round" fill="none" />
          <circle cx={x + s * 12} cy={y0 + 10} r={5} fill={C.steelEdge} />
        </g>
      ))}
    </g>
  );
};

export const RigView: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const r = T.rig(frame);
  const R = L.rig;
  return (
    <>
      <div style={{ position: "absolute", left: L.header.x, top: L.header.y, fontFamily: FONT.mono, fontWeight: 500, fontSize: L.header.size, letterSpacing: 2.5,
        color: C.steelLit, whiteSpace: "nowrap" }}>
        {T.rigInfo.header}
      </div>
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
        <rect x={R.x0} y={R.railY - 9} width={R.x1 - R.x0} height={18} rx={9} fill={C.steel} stroke={C.steelEdge} strokeWidth={3} />
        <rect x={R.x0 + 6} y={R.railY - 6} width={R.x1 - R.x0 - 12} height={4} rx={2} fill={rgba(C.steelLit, 0.8)} />
        {[R.x0 + 20, R.x1 - 20].map((x) => <circle key={x} cx={x} cy={R.railY} r={4} fill={C.steelEdge} />)}
        <ClampJaws x={R.clampX} y0={R.railY + 10} y1={R.jawY} open={r.clamp} />
        {r.floor > 0 ? (
          <g opacity={r.floor}>
            <rect x={L.win.x0} y={r.floorY} width={L.field.x1 - L.win.x0} height={26} fill={rgba(C.drapeDeep, 0.55)} />
            <line x1={L.win.x0} y1={r.floorY} x2={L.field.x1} y2={r.floorY} stroke={C.steel} strokeWidth={5} strokeLinecap="round" />
          </g>
        ) : null}
      </svg>
    </>
  );
};

/** ROOT (overlay plane): 'drawn · not to scale' for the drawn cat + rig, from frame 0 until the ledger takes the stage */
export const DrawnTagLive: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const v = T.rig(frame).drawnTag;
  if (v <= 0) return null;
  return (
    <div style={{ position: "absolute", left: L.drawnTag.x, top: L.drawnTag.y, height: 38, padding: "0 12px", display: "flex", alignItems: "center",
      backgroundColor: rgba(C.shadow, 0.82), borderRadius: 6, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.bone, whiteSpace: "nowrap", opacity: v }}>
      {T.labels.drawn}
    </div>
  );
};
