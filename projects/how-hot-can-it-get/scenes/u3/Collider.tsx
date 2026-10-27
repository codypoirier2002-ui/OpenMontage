// sc07 · Collider · U3. The root crossfades the window K2 -> S4 ('AI illustration', root tag). U3 draws, INSIDE the window
// (clipped to its rounded box): two thin DRAWN beam lines that run in from the window's left and right edges along the
// detector's centre line, their heads accelerating (gravity ease-in: still ~26 px apart on beamFlash - 1) and meeting ON
// T.sfx.beamFlash (X6 thump peak) with a flash, then a sparse spray of curved drawn tracks that fades out before the rail
// compresses (T.sfx.compress). Colour = the glow's black-body colour (T.glow(f).rgb), lifted toward white.
// Tag 'drawn' shares the beams' first visible frame (lesson 31). Hooks at the top (lesson 1). No blend modes (lesson 24).
import React, { useId } from "react";
import { useCurrentFrame } from "remotion";
import { lighten } from "../../shared/blackbody";
import { cssId, rnd } from "../../shared/noise";
import { SceneTag } from "../../overlay/Tag";
import { L } from "../../theme";
import { prog, useT } from "../../time";
import type { Timing } from "../../time";
import type { Mount, SceneProps } from "../../types";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const TAG_TEXT = "drawn";
const B = L.window;
const WW = B.x1 - B.x0;
const WH = B.y1 - B.y0;
/** the detector centre (S4's ring centre is fitted to the window centre: prepare_media.py) in window-local px */
const CX = WW / 2;
const CY = WH / 2;
const N_TRACKS = 22;
/** a Forge Black under-stroke so the drawn lines read over the bright silver plate */
const DARK = "rgba(11,9,7,0.55)";

/** the beam schedule: in from the beams' start, meeting on the flash; debris drawn after it, gone by the compress */
const beats = (T: Timing) => {
  const flash = T.sfx.beamFlash;
  const start = T.at("s4", "lead");
  const gone = T.sfx.compress - 2;
  return { flash, start, gone };
};

const rgbCss = (c: [number, number, number], a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

export const Collider: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const blurId = cssId(useId(), "beamblur");
  if (frame < from || frame >= to) return null;
  const { flash, start, gone } = beats(T);
  if (frame < start) return null;
  const g = T.glow(frame);
  const hot = lighten(g.rgb, 0.55);
  const white = lighten(g.rgb, 0.85);

  // the heads: gravity ease-in (x^2) so they are visibly still moving on flash - 1 and touch ON flash
  const p = prog(frame, start, flash);
  const k = p * p;
  const margin = 10;
  const lx = margin + (CX - margin) * k;
  const rx = WW - margin - (WW - margin - CX) * k;
  // the beam lines: draw in, stay as faint lines after the flash, fade out with the debris
  const out = 1 - prog(frame, gone - 14, gone);
  const lineA = (frame < flash ? 0.95 : 0.55 * (1 - prog(frame, flash, flash + 24))) * out;
  const headA = frame < flash ? 1 : 0;
  // the flash: full ON the flash frame, decaying
  const fl = frame >= flash ? Math.exp(-(frame - flash) / 6) : 0;
  // the debris: tracks grow out over 14 f from the flash, fade by `gone`
  const grow = prog(frame, flash, flash + 14, (x) => 1 - (1 - x) * (1 - x));
  const debrisA = frame >= flash ? out * (1 - 0.35 * prog(frame, flash + 14, gone - 14)) : 0;

  const tracks: React.ReactNode[] = [];
  if (frame >= flash) {
    for (let i = 0; i < N_TRACKS; i++) {
      const a0 = 2 * Math.PI * (i / N_TRACKS + 0.6 * rnd("u3-trk-a", i) / N_TRACKS);
      const len = 120 + 230 * rnd("u3-trk-l", i);
      const curv = (rnd("u3-trk-c", i) * 2 - 1) * 0.0045; // radians per px: charged tracks curl in the field
      const steps = 24;
      let x = CX;
      let y = CY;
      let a = a0;
      let d = `M ${x.toFixed(1)} ${y.toFixed(1)}`;
      const L_ = len * grow;
      for (let s = 1; s <= steps; s++) {
        const ds = L_ / steps;
        a += curv * ds;
        x += Math.cos(a) * ds;
        y += Math.sin(a) * ds;
        d += ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
      }
      const w = 2.2 + 1.6 * rnd("u3-trk-w", i);
      tracks.push(
        <g key={i}>
          <path d={d} stroke={DARK} strokeWidth={w + 4} fill="none" strokeLinecap="round" />
          <path d={d} stroke={rgbCss(hot, 0.95)} strokeWidth={w} fill="none" strokeLinecap="round" />
        </g>,
      );
    }
  }

  return (
    <div style={{ position: "absolute", left: B.x0, top: B.y0, width: WW, height: WH, borderRadius: B.r, overflow: "hidden" }}>
      <svg width={WW} height={WH} style={{ position: "absolute", left: 0, top: 0 }}>
        <defs>
          <filter id={blurId} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation={6} />
          </filter>
        </defs>
        {/* beam lines (glow copy + core), left and right */}
        {lineA > 0 ? (
          <g opacity={lineA}>
            <line x1={0} y1={CY} x2={lx} y2={CY} stroke={rgbCss(g.rgb, 0.9)} strokeWidth={9} filter={`url(#${blurId})`} />
            <line x1={WW} y1={CY} x2={rx} y2={CY} stroke={rgbCss(g.rgb, 0.9)} strokeWidth={9} filter={`url(#${blurId})`} />
            <line x1={0} y1={CY} x2={lx} y2={CY} stroke={DARK} strokeWidth={8} strokeLinecap="round" />
            <line x1={WW} y1={CY} x2={rx} y2={CY} stroke={DARK} strokeWidth={8} strokeLinecap="round" />
            <line x1={0} y1={CY} x2={lx} y2={CY} stroke={rgbCss(white)} strokeWidth={4} strokeLinecap="round" />
            <line x1={WW} y1={CY} x2={rx} y2={CY} stroke={rgbCss(white)} strokeWidth={4} strokeLinecap="round" />
          </g>
        ) : null}
        {/* the beam heads (bunches) */}
        {headA > 0 ? (
          <g>
            <circle cx={lx} cy={CY} r={13} fill={rgbCss(g.rgb, 0.9)} filter={`url(#${blurId})`} />
            <circle cx={rx} cy={CY} r={13} fill={rgbCss(g.rgb, 0.9)} filter={`url(#${blurId})`} />
            <circle cx={lx} cy={CY} r={5.5} fill={rgbCss(white)} />
            <circle cx={rx} cy={CY} r={5.5} fill={rgbCss(white)} />
          </g>
        ) : null}
        {/* the debris spray */}
        {debrisA > 0 ? <g opacity={debrisA}>{tracks}</g> : null}
        {/* the flash */}
        {fl > 0.01 ? (
          <g opacity={out}>
            <circle cx={CX} cy={CY} r={40 + 150 * (1 - fl)} fill={rgbCss(g.rgb, 0.55 * fl)} filter={`url(#${blurId})`} />
            <circle cx={CX} cy={CY} r={70 * fl + 8} fill={rgbCss(hot, 0.9 * fl)} filter={`url(#${blurId})`} />
            <circle cx={CX} cy={CY} r={22 * fl + 4} fill={rgbCss(white, Math.min(1, fl * 1.2))} />
          </g>
        ) : null}
      </svg>
    </div>
  );
};

/** 'drawn' (bottom-left inside the window: the 'AI illustration' root tag owns the bottom-right) from the beams' first frame */
export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const T = useT();
  const { start, gone } = beats(T);
  return <SceneTag x={B.x0 + 16} y={B.y1 - 54} enter={Math.max(from, start)} exit={Math.min(to, gone)} text={TAG_TEXT} />;
};
