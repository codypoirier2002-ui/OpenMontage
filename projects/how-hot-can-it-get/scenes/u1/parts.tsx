// U1 unit-local helpers (pure components, NO hooks): the hero rung card (a Forge Black plate behind <RungLabel> + a thin
// leader from the root rung tick) and the drawn lead ingot (unlit grey; slumps into a puddle - lead melts at 327 °C,
// far below the first visible glow, so it never glows: no warm colour, no halo).
import React from "react";
import { C, L, rgba } from "../../theme";
import { measure, RungLabel } from "../../shared/Type";

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** the hero card: number centre line at (x + pad, y); leader from the rung tick (L.rail.tickX1, tickY) to the card */
export const HeroCard: React.FC<{
  x: number; y: number; num: string; label: string; tickY: number; dy: number; opacity: number; size?: number; labelSize?: number;
}> = ({ x, y, num, label, tickY, dy, opacity, size = 96, labelSize = 34 }) => {
  const pad = 16;
  const w = Math.max(measure(num, "display", size), measure(label, "mono", labelSize)) + pad * 2;
  const top = y - size * 0.55 + 4;
  const h = size * 1.1 + labelSize * 1.2 + size * 0.02 + pad - 6;
  const cardTop = top - pad + 8 + dy;
  const cardBot = cardTop + h;
  // leader: from the tick's right end to the nearest point on the card's left edge
  const ly = Math.max(cardTop + 14, Math.min(cardBot - 14, tickY));
  const x0 = L.rail.tickX1 + 2;
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: L.W, height: L.H, opacity }}>
      <svg width={L.W} height={L.H} style={{ position: "absolute", left: 0, top: 0 }}>
        <path d={`M ${x0} ${tickY} L ${x0 + 12} ${tickY} L ${x} ${ly}`} stroke={rgba(C.bone, 0.75)} strokeWidth={2} fill="none" />
        <circle cx={x} cy={ly} r={3.5} fill={C.bone} />
      </svg>
      <div style={{ position: "absolute", left: x, top: cardTop, width: w, height: h, borderRadius: 14, backgroundColor: rgba(C.forge, 0.8),
        border: `1.5px solid ${rgba(C.ironLit, 0.9)}` }} />
      <RungLabel x={x + pad} y={y} num={num} label={label} size={size} labelSize={labelSize} dy={dy} labelColor={C.bone} />
    </div>
  );
};

/**
 * the drawn lead ingot, base centred on (cx, by); melt 0..1 = solid trapezoid bar -> flat puddle (same area, roughly).
 * Lead-grey, unlit: a front face, a top face and a cool edge sheen (reflection, not light).
 */
export const Ingot: React.FC<{ cx: number; by: number; melt: number; dy: number; opacity: number }> = ({ cx, by, melt, dy, opacity }) => {
  const t = Math.max(0, Math.min(1, melt));
  const wb = lerp(150, 232, t); // bottom width
  const wt = lerp(118, 200, t); // top width (front face)
  const h = lerp(46, 9, t); // front-face height
  const d = lerp(20, 3, t); // top-face depth (perspective lift)
  const r = lerp(3, h, t * t); // top corners round off into a blob
  const b = by + dy;
  const xl = cx - wb / 2;
  const xr = cx + wb / 2;
  const tl = cx - wt / 2;
  const tr = cx + wt / 2;
  const ty = b - h;
  const rr = Math.min(r, h, (wt / 2) * 0.9);
  const front = `M ${xl} ${b} L ${tl} ${ty + rr} Q ${tl} ${ty} ${tl + rr} ${ty} L ${tr - rr} ${ty} Q ${tr} ${ty} ${tr} ${ty + rr} L ${xr} ${b} Z`;
  const top = `M ${tl + rr * 0.6} ${ty} L ${tl + d * 0.8 + rr * 0.3} ${ty - d} L ${tr - d * 0.4 - rr * 0.3} ${ty - d} L ${tr - rr * 0.6} ${ty} Z`;
  // the spreading pool under the bar (appears as it slumps)
  const poolW = lerp(wb * 0.9, wb * 1.18, t);
  const poolH = lerp(4, 16, t);
  return (
    <svg width={L.W} height={L.H} style={{ position: "absolute", left: 0, top: 0, opacity }}>
      <ellipse cx={cx} cy={b + 2} rx={poolW / 2 + 10} ry={poolH / 2 + 6} fill={rgba(C.forge, 0.55)} />
      {t > 0 ? <ellipse cx={cx + 6} cy={b - 1} rx={poolW / 2} ry={poolH / 2} fill="#5F6064" opacity={Math.min(1, t * 2)} /> : null}
      <path d={front} fill="#6C6D71" stroke="#3A3B3E" strokeWidth={2} strokeLinejoin="round" />
      {d > 2 ? <path d={top} fill="#8E9095" stroke="#3A3B3E" strokeWidth={1.5} strokeLinejoin="round" /> : null}
      <path d={`M ${tl + rr + 6} ${ty + 6} L ${tr - rr - 6} ${ty + 6}`} stroke="#B9BBC0" strokeOpacity={0.45} strokeWidth={2} strokeLinecap="round" />
    </svg>
  );
};
