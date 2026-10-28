// U1 helpers. Hooks at the top (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import { C, L } from "../../theme";
import { useT } from "../../time";

const R = L.rail;

/** sc01: a glint riding the bright rail's draw head (railDraw 0 -> 1, bottom -> top) */
export const RailGlint: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const d = T.ladder(frame).railDraw;
  if (d <= 0 || d >= 1) return null;
  const y = R.y1 - (R.y1 - R.y0) * d;
  const a = Math.min(1, (1 - d) / 0.1) * Math.min(1, d / 0.04);
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
      <line x1={R.x} y1={y + 2} x2={R.x} y2={Math.min(R.y1, y + 70)} stroke={C.bone} strokeWidth={5} strokeLinecap="round" opacity={0.22 * a} />
      <circle cx={R.x} cy={y} r={11} fill={C.steel} opacity={0.22 * a} />
      <circle cx={R.x} cy={y} r={4.5} fill={C.bone} opacity={0.95 * a} />
    </svg>
  );
};
