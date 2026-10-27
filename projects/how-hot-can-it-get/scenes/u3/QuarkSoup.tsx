// sc09 · QuarkSoup · U3. Root: the window dims to 0.8 over S4 (T.sfx.soupStart), X2 soft rising hiss. U3 draws INSIDE
// the window (clipped to its rounded box), all illustrative: a proton = three quark dots (red / green / blue, the colour-
// charge convention) held by wavy gluon springs in a glowing bag lit in the glow's black-body blue-white (T.glow). On
// 'melt' (T.sfx.protonMelt) the bag loosens and swells away, the springs stretch and fade, its quarks drift free, and
// more quarks + gluon squiggles fill the window: a shimmering soup, complete by 'soup' (T.at('s4','soup')), where the
// label 'quark-gluon plasma' appears. Tag 'drawn · illustrative' from the proton's first frame. Everything is out by the
// scene end (the root closes the window from there). Seeded (rnd / noise1) only. Hooks at the top (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import { lighten } from "../../shared/blackbody";
import { noise1, rnd } from "../../shared/noise";
import { Label } from "../../shared/Type";
import { SceneTag } from "../../overlay/Tag";
import { C, E, L } from "../../theme";
import { prog, useT } from "../../time";
import type { Timing } from "../../time";
import type { Mount, SceneProps } from "../../types";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const TAG_TEXT = "drawn · illustrative";
const LABEL_TEXT = "quark-gluon plasma";
const B = L.window;
const WW = B.x1 - B.x0;
const WH = B.y1 - B.y0;
const CX = WW / 2;
const CY = WH / 2 - 10;
const BAG_R = 118;
const N_SOUP = 84;
const N_GLUON = 26;
/** colour charges (drawn convention): red, green, blue */
const QC: [number, number, number][] = [
  [240, 84, 84],
  [84, 206, 116],
  [96, 136, 255],
];
const css = (c: [number, number, number], a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

const beats = (T: Timing, from: number, to: number) => ({
  melt: T.sfx.protonMelt,
  soup: T.at("s4", "soup"),
  exitFrom: to - 10,
  from,
  to,
});

/** a wavy gluon spring from a to b */
const spring = (ax: number, ay: number, bx: number, by: number, waves: number, amp: number, phase: number) => {
  const dx = bx - ax;
  const dy = by - ay;
  const len = Math.hypot(dx, dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;
  const n = 40;
  let d = "";
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const o = amp * Math.sin(2 * Math.PI * waves * t + phase) * Math.sin(Math.PI * t);
    d += `${i ? " L" : "M"} ${(ax + dx * t + nx * o).toFixed(1)} ${(ay + dy * t + ny * o).toFixed(1)}`;
  }
  return d;
};

const Quark: React.FC<{ x: number; y: number; r: number; c: [number, number, number]; a: number }> = ({ x, y, r, c, a }) => (
  <g opacity={a}>
    <circle cx={x} cy={y} r={r * 2.1} fill={css(c, 0.22)} />
    <circle cx={x} cy={y} r={r} fill={css(c)} />
    <circle cx={x - r * 0.3} cy={y - r * 0.3} r={r * 0.38} fill={css(lighten(c, 0.6), 0.9)} />
  </g>
);

export const QuarkSoup: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  const { melt, soup, exitFrom } = beats(T, from, to);
  const g = T.glow(frame);
  const lit = lighten(g.rgb, 0.5);
  const white = lighten(g.rgb, 0.85);
  const fadeIn = prog(frame, from - 2, from + 6);
  const out = 1 - prog(frame, exitFrom, to);
  const m = prog(frame, melt, soup, E.calm); // the melt 0..1
  const t = frame / 30;

  // the proton's three quarks: a triangle, jiggling; drifting free with the melt
  const pq = [0, 1, 2].map((i) => {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / 3;
    const bx = CX + 50 * Math.cos(a) + 9 * noise1(`u3-pq-x${i}`, frame / 7);
    const by = CY + 50 * Math.sin(a) + 9 * noise1(`u3-pq-y${i}`, frame / 7);
    const fx = CX + (170 + 40 * i) * Math.cos(a + 0.5) + 18 * noise1(`u3-pf-x${i}`, frame / 18);
    const fy = CY + (130 + 30 * i) * Math.sin(a + 0.5) + 18 * noise1(`u3-pf-y${i}`, frame / 18);
    return { x: bx + (fx - bx) * m, y: by + (fy - by) * m, c: QC[i] };
  });
  // the bag: swells, wobbles and fades with the melt
  const bagR = BAG_R * (1 + 1.3 * m) + 4 * Math.sin(t * 5);
  const bagA = (1 - m) * fadeIn;
  // a pre-melt quiver as it heats ('hot' -> 'melt')
  const quiver = prog(frame, T.at("s4", "hot"), melt);
  const bagPath = (() => {
    const n = 48;
    let d = "";
    for (let i = 0; i <= n; i++) {
      const a = (2 * Math.PI * i) / n;
      const w = (0.035 * quiver + 0.12 * m) * noise1(`u3-bag${i % n}`, frame / 4 + i * 0.37);
      const r = bagR * (1 + w);
      d += `${i ? " L" : "M"} ${(CX + r * Math.cos(a)).toFixed(1)} ${(CY + r * Math.sin(a)).toFixed(1)}`;
    }
    return d + " Z";
  })();

  // the soup: quarks fading in (staggered with the melt), emerging from around the proton outward, then jostling
  const soupQ: React.ReactNode[] = [];
  for (let i = 0; i < N_SOUP; i++) {
    const thr = 0.1 + 0.75 * rnd("u3-sq-t", i);
    const a = Math.min(1, Math.max(0, (m - thr) / 0.18)) * Math.min(1, Math.max(0, (frame >= soup ? 1 : 0) + m * 1.2));
    if (a <= 0) continue;
    const tx = 40 + (WW - 80) * rnd("u3-sq-x", i);
    const ty0 = 40 + (WH - 150) * rnd("u3-sq-y", i);
    // keep clear of the root zeros chip (window top-left, local x < ~190, y < ~85)
    const ty = tx < 230 && ty0 < 110 ? ty0 + 110 : ty0;
    const e = E.open(Math.min(1, Math.max(0, (m - thr) / 0.3)));
    const x = CX + (tx - CX) * (0.55 + 0.45 * e) + 22 * noise1(`u3-sq-jx${i}`, frame / 16);
    const y = CY + (ty - CY) * (0.55 + 0.45 * e) + 22 * noise1(`u3-sq-jy${i}`, frame / 16);
    soupQ.push(<Quark key={i} x={x} y={y} r={6 + 2.5 * rnd("u3-sq-r", i)} c={QC[i % 3]} a={a} />);
  }
  const gl: React.ReactNode[] = [];
  for (let i = 0; i < N_GLUON; i++) {
    const thr = 0.2 + 0.7 * rnd("u3-gl-t", i);
    const a = Math.min(1, Math.max(0, (m - thr) / 0.2));
    if (a <= 0) continue;
    const x = 50 + (WW - 100) * rnd("u3-gl-x", i) + 18 * noise1(`u3-gl-jx${i}`, frame / 14);
    const gy0 = 50 + (WH - 170) * rnd("u3-gl-y", i);
    const y = (x < 240 && gy0 < 120 ? gy0 + 120 : gy0) + 18 * noise1(`u3-gl-jy${i}`, frame / 14);
    const ang = 2 * Math.PI * rnd("u3-gl-a", i) + 0.4 * noise1(`u3-gl-r${i}`, frame / 20);
    const len = 34 + 26 * rnd("u3-gl-l", i);
    const flick = 0.55 + 0.45 * (0.5 + 0.5 * noise1(`u3-gl-f${i}`, frame / 3));
    gl.push(
      <path key={i} d={spring(x, y, x + len * Math.cos(ang), y + len * Math.sin(ang), 3, 5, frame * 0.5 + i)} stroke={css(white, 0.8)} strokeWidth={2.2}
        fill="none" strokeLinecap="round" opacity={a * flick} />,
    );
  }
  // the hot haze in the glow colour, rising with the melt (a shimmer, no blend modes)
  const hazeA = (0.1 + 0.32 * m) * fadeIn;
  const shimmer = 0.85 + 0.15 * noise1("u3-haze", frame / 5);

  return (
    <div style={{ position: "absolute", left: B.x0, top: B.y0, width: WW, height: WH, borderRadius: B.r, overflow: "hidden", opacity: out }}>
      <div style={{ position: "absolute", inset: 0, opacity: hazeA * shimmer,
        background: `radial-gradient(ellipse ${180 + 260 * m}px ${170 + 200 * m}px at ${CX}px ${CY}px, ${css(lit, 0.75)} 0%, ${css(g.rgb, 0.3)} 55%, ${css(g.rgb, 0)} 100%)` }} />
      <svg width={WW} height={WH} style={{ position: "absolute", left: 0, top: 0 }}>
        {/* the bag */}
        {bagA > 0.003 ? (
          <g opacity={bagA}>
            <path d={bagPath} fill={css(g.rgb, 0.16)} stroke={css(lit, 0.9)} strokeWidth={3} />
            <path d={bagPath} fill="none" stroke={css(g.rgb, 0.35)} strokeWidth={14} />
          </g>
        ) : null}
        {/* the soup's gluons and quarks */}
        {gl}
        {soupQ}
        {/* the proton's springs (stretching, fading) and its three quarks */}
        <g opacity={fadeIn * (1 - m)}>
          {[0, 1, 2].map((i) => {
            const a = pq[i];
            const b = pq[(i + 1) % 3];
            return <path key={i} d={spring(a.x, a.y, b.x, b.y, 4, 6, frame * 0.45 + i * 2)} stroke={css(white, 0.9)} strokeWidth={2.6} fill="none" strokeLinecap="round" />;
          })}
        </g>
        {pq.map((q, i) => (
          <Quark key={`p${i}`} x={q.x} y={q.y} r={12} c={q.c} a={fadeIn} />
        ))}
      </svg>
    </div>
  );
};

/** 'drawn · illustrative' (bottom-left inside the window) from the proton's first frame; 'quark-gluon plasma' on 'soup' */
export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const soup = T.at("s4", "soup");
  const a = prog(frame, soup - 4, soup) * (1 - prog(frame, to - 10, to));
  return (
    <>
      <SceneTag x={B.x0 + 16} y={B.y1 - 54} enter={from} exit={to} text={TAG_TEXT} />
      {frame >= soup - 4 && frame < to ? (
        <Label x={(B.x0 + B.x1) / 2} y={B.y1 - 108} text={LABEL_TEXT} size={30} weight={500} anchor="center" variant="chip" color={C.bone} opacity={a} />
      ) : null}
    </>
  );
};
