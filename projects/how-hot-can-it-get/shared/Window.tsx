// THE WINDOW (ROOT ONLY for the four AI plates: Composition.tsx mounts <WindowView/> once; props.window, build_props.py;
// the AI tags are root too: <WindowTags/> on the overlay plane, keyed to each plate's ACTUAL visibility).
//   x 220-920, y 360-900, rounded 28 px, a soft Iron frame (6 px Iron + a 1 px lit rim + a warm inner shadow)
//   K1  sc03        Death Valley heat shimmer, FORWARD only (Kling's forward glide must never reverse), + a code push
//                   1.00 -> 1.02; the labelled thermal FALSE-COLOUR view (an inferno-style LUT on the clip's own luma,
//                   SVG filter) fades in on 'degrees' ('false colour' tag) - nothing this cool glows (art direction)
//   S2  sc04        Venus, crossfades in at the scene start (the false colour clears with it), push 1.00 -> 1.04; the
//                   rocks are sky-lit and do NOT glow: no glow / grade is added
//   K2  sc06        the plasma ring, FORWARD then the LAST FRAME HOLDS (sc06 is longer than the clip; no ping-pong: the
//                   push-in would reverse) under a code push 1.00 -> 1.03 so the hold never reads as a freeze
//   S4  sc07-sc09   the collider (generic 'AI illustration' tag only: it resembles a real detector; never name one),
//                   push 1.00 -> 1.05; DIMMED (Forge Black over the plate) for U3's drawings: 0.55 in sc08, 0.8 in sc09
// The window opens over 6 f (ease-out, first visible frame ON its sound) and closes over 8 f (ease-in-out): scale 0.96 -> 1 + fade. Clip frames are exact (Freeze + OffthreadVideo,
// the video 11 / 12 pattern); before `start` the staged first frame shows, after the last staged frame the last one.
// <WindowFrame/> is exported for builders who need the window's frame look around their OWN drawings (not for AI media:
// every AI plate goes through props.window so the root tags it). Hooks at the top (lesson 1).

import React, { useId } from "react";
import { Freeze, Img, OffthreadVideo, staticFile, useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { prog, useT } from "../time";
import type { Timing } from "../time";
import type { WindowMedia } from "../types";
import { cssId } from "./noise";

/** inferno-style thermal LUT (8 stops, sRGB 0..1) applied to the clip's luma */
const LUT = [
  [0.0, 0.0, 0.02], [0.16, 0.04, 0.33], [0.4, 0.08, 0.43], [0.62, 0.16, 0.39], [0.83, 0.28, 0.26], [0.96, 0.49, 0.08], [0.98, 0.76, 0.15], [0.99, 1.0, 0.64],
];
const SKY_COLD = `rgb(${LUT[1].map((v) => Math.round(v * 255)).join(",")})`;
const table = (ch: number) => LUT.map((s) => s[ch].toFixed(3)).join(" ");

/** the plate's visibility at `frame` (1 = fully shown; the incoming plate of a crossfade ramps over xf, drawn on top) */
export const mediaAlpha = (T: Timing, m: WindowMedia, frame: number) => {
  if (frame < m.from || frame >= m.to + m.xf) return 0;
  const list = T.windowInfo.media;
  const i = list.findIndex((x) => x.id === m.id);
  const prev = i > 0 ? list[i - 1] : null;
  const crossIn = prev !== null && prev.to === m.from;
  return crossIn ? prog(frame, m.from, m.from + m.xf) : 1;
};

/** the clip frame of a plate at `frame` (null = show `first`; -1 = show `last`, the held end) */
export const mediaClipFrame = (m: WindowMedia, frame: number): number | null => {
  if (m.kind === "still" || frame < m.start) return null;
  const n = Math.round(frame - m.start);
  return n >= m.frames - 1 ? -1 : Math.max(0, n);
};

export const WindowFrame: React.FC<{ open: number; children?: React.ReactNode }> = ({ open, children }) => {
  const b = L.window;
  const w = b.x1 - b.x0;
  const h = b.y1 - b.y0;
  const k = Math.max(0, Math.min(1, open)); // the ease lives in props.window.open (QA B10: no second ease on top)
  return (
    <div style={{ position: "absolute", left: b.x0, top: b.y0, width: w, height: h, opacity: k, transform: `scale(${0.96 + 0.04 * k})`, transformOrigin: "50% 50%" }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: b.r, overflow: "hidden", backgroundColor: C.forge, boxShadow: "0 18px 50px rgba(0,0,0,0.6)" }}>
        {children}
        <div style={{ position: "absolute", inset: 0, borderRadius: b.r, boxShadow: "inset 0 0 40px rgba(11,9,7,0.55)" }} />
      </div>
      <div style={{ position: "absolute", inset: -b.frame / 2, borderRadius: b.r + b.frame / 2, border: `${b.frame}px solid ${C.iron}` }} />
      <div style={{ position: "absolute", inset: b.frame / 2, borderRadius: b.r - b.frame / 2, border: `1px solid ${rgba(C.ironLit, 0.7)}` }} />
    </div>
  );
};

const Plate: React.FC<{ m: WindowMedia; frame: number; lutId?: string }> = ({ m, frame, lutId }) => {
  const b = L.window;
  const push = m.push[0] + (m.push[1] - m.push[0]) * prog(frame, m.from, m.to + m.xf);
  const bw = b.x1 - b.x0;
  const bh = b.y1 - b.y0;
  const style: React.CSSProperties = {
    position: "absolute", left: m.fit.left - b.x0, top: m.fit.top - b.y0, width: m.fit.w * m.fit.scale, height: m.fit.h * m.fit.scale,
    transform: `scale(${push})`, transformOrigin: `${bw / 2 - (m.fit.left - b.x0)}px ${bh / 2 - (m.fit.top - b.y0)}px`,
    filter: lutId ? `url(#${lutId})` : undefined,
  };
  const cf = mediaClipFrame(m, frame);
  if (cf === null) return <Img src={staticFile(m.kind === "still" ? m.src : m.first)} style={style} />;
  // the held end uses the SAME decoder path as the moving clip (no JPEG swap: no one-frame step on the hold)
  return (
    <div style={style}>
      <Freeze frame={cf === -1 ? m.frames - 1 : cf}>
        <OffthreadVideo src={staticFile(m.src)} muted style={{ width: "100%", height: "100%" }} />
      </Freeze>
    </div>
  );
};

/** ROOT: the window and its plates while it is open */
export const WindowView: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const lutId = cssId(useId(), "lut");
  const w = T.win(frame);
  if (w.open <= 0) return null;
  const live = T.windowInfo.media.map((m) => ({ m, a: mediaAlpha(T, m, frame) })).filter((x) => x.a > 0);
  return (
    <>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id={lutId} colorInterpolationFilters="sRGB">
          <feColorMatrix type="matrix" values="0.2126 0.7152 0.0722 0 0  0.2126 0.7152 0.0722 0 0  0.2126 0.7152 0.0722 0 0  0 0 0 1 0" />
          <feComponentTransfer>
            <feFuncR type="table" tableValues={table(0)} />
            <feFuncG type="table" tableValues={table(1)} />
            <feFuncB type="table" tableValues={table(2)} />
          </feComponentTransfer>
        </filter>
      </svg>
      <WindowFrame open={w.open}>
        {live.map(({ m, a }) => (
          <div key={m.id} style={{ position: "absolute", inset: 0, opacity: a }}>
            <Plate m={m} frame={frame} />
            {m.id === "K1" && w.lut > 0 ? (
              <div style={{ position: "absolute", inset: 0, opacity: w.lut }}>
                <Plate m={m} frame={frame} lutId={lutId} />
                {/* QA B7: a clear sky is COLD in a thermal view: everything above the ridge takes the LUT's cool end (the ground stays hot) */}
                <div style={{ position: "absolute", inset: 0, backgroundColor: SKY_COLD,
                  WebkitMaskImage: "linear-gradient(to bottom, #000 0px, #000 100px, transparent 170px)",
                  maskImage: "linear-gradient(to bottom, #000 0px, #000 100px, transparent 170px)" }} />
              </div>
            ) : null}
          </div>
        ))}
        {w.dim > 0 ? <div style={{ position: "absolute", inset: 0, backgroundColor: C.forge, opacity: w.dim }} /> : null}
      </WindowFrame>
    </>
  );
};

/** ROOT (overlay plane): the plates' AI tags + the 'false colour' tag, each tied to its element's actual visibility (lesson 31:
 *  a tag shares its graphic's first frame; in a crossfade the outgoing tag fades as the incoming one rises) */
export const WindowTags: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const w = T.win(frame);
  if (w.open <= 0) return null;
  const b = L.window;
  const k = Math.max(0, Math.min(1, w.open));
  const list = T.windowInfo.media;
  const out: React.ReactNode[] = [];
  // QA B4: across a plate crossfade the tag CUTS at the crossfade's midpoint (one tag slot, one text, a tag on EVERY frame an
  // AI plate is visible), never two texts dissolving in one slot
  list.forEach((m, i) => {
    let a = mediaAlpha(T, m, frame);
    const prev = i > 0 ? list[i - 1] : null;
    const next = list[i + 1];
    if (prev && prev.to === m.from) a = frame >= m.from + Math.floor(m.xf / 2) ? 1 : 0;
    if (next && next.from === m.to && frame >= next.from) a = frame < next.from + Math.floor(next.xf / 2) ? 1 : 0;
    if (frame < m.from || frame >= m.to + m.xf) a = 0;
    if (a <= 0) return;
    out.push(<WinTag key={m.id} text={m.tag} right={b.x1 - 16} y={b.y1 - 54} opacity={a * k} />);
  });
  if (w.lut > 0) out.push(<WinTag key="lut" text={T.windowInfo.lutTag} left={b.x0 + 16} y={b.y1 - 54} opacity={Math.min(1, w.lut * 1.5) * k} />);
  return <>{out}</>;
};

const WinTag: React.FC<{ text: string; left?: number; right?: number; y: number; opacity: number }> = ({ text, left, right, y, opacity }) => (
  <div style={{ position: "absolute", left: left ?? undefined, right: right !== undefined ? L.W - right : undefined, top: y, height: 38, padding: "0 12px",
    display: "flex", alignItems: "center", backgroundColor: rgba(C.forge, 0.78), borderRadius: 6, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24,
    color: C.bone, whiteSpace: "nowrap", opacity }}>
    {text}
  </div>
);
