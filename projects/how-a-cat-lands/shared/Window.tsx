// THE WINDOW (ROOT ONLY: Composition.tsx mounts <WindowView/> once; props.window, build_props.py; its tag is root too:
// <WindowTags/> on the overlay plane). ONE portrait box (L.win x 160-620, y 360-1000, left of the checklist card - never over
// it) shared by three plates, each with its own alpha[f]:
//   S1  sc02       the AI still of the cat upside down in midair (prepare_media.py crop), push 1.00 -> 1.03
//   A1  sc03       the 1894 engraving after Marey as a vertical FILM STRIP (shared/Strip.tsx), stepping one cell at a time
//   S2  sc09       the AI still of a cat landing on all four (crop), push 1.00 -> 1.03, in the landing beat after 'four.'
// open[f] = the frame's visibility: the first visible frame is its key frame (out-quad over WINDOW_OPEN_F), the close is
// ease-in-out over WINDOW_CLOSE_F; scale 0.96 -> 1 with the open value. S1 -> A1 CROSSFADE over XFADE_F; the TAG is the
// plate with the larger alpha: a HARD swap at the midpoint (lesson 38: exactly one tag on every visible frame, asserted).
// <WindowFrame/> is exported for builders who need the window look around their OWN drawings (never for AI / archival
// media: those go through props.window so the root tags them). Hooks at the top (lesson 1).

import React from "react";
import { Img, staticFile, useCurrentFrame } from "remotion";
import { C, FONT, rgba } from "../theme";
import { prog, useT } from "../time";
import type { Rect, WindowPlate } from "../types";
import { MareyStrip } from "./Strip";
import { measure } from "./Type";

export const WindowFrame: React.FC<{ box: Rect; open: number; radius?: number; frame?: number; children?: React.ReactNode }> = ({ box, open, radius = 22, frame = 6, children }) => {
  const w = box.x1 - box.x0;
  const h = box.y1 - box.y0;
  const k = Math.max(0, Math.min(1, open));
  return (
    <div style={{ position: "absolute", left: box.x0, top: box.y0, width: w, height: h, opacity: k, transform: `scale(${0.96 + 0.04 * k})`, transformOrigin: "50% 50%" }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: radius, overflow: "hidden", backgroundColor: C.shadow, boxShadow: "0 18px 40px rgba(14,20,26,0.55)" }}>
        {children}
        <div style={{ position: "absolute", inset: 0, borderRadius: radius, boxShadow: "inset 0 0 30px rgba(14,20,26,0.45)" }} />
      </div>
      <div style={{ position: "absolute", inset: -frame / 2, borderRadius: radius + frame / 2, border: `${frame}px solid ${C.steelEdge}` }} />
      <div style={{ position: "absolute", inset: frame / 2, borderRadius: radius - frame / 2, border: `1px solid ${rgba(C.steelLit, 0.8)}` }} />
    </div>
  );
};

const Plate: React.FC<{ m: WindowPlate; frame: number; w: number; h: number; alpha: number; step: number }> = ({ m, frame, w, h, alpha, step }) => {
  const push = m.push[0] + (m.push[1] - m.push[0]) * prog(frame, m.pushFrom, m.pushTo);
  const full: React.CSSProperties = { position: "absolute", left: 0, top: 0, width: w, height: h };
  return (
    <div style={{ ...full, opacity: alpha, transform: `scale(${push})`, transformOrigin: "50% 50%" }}>
      {m.base ? <Img src={staticFile(m.base)} style={full} /> : null}
      {m.cells ? <MareyStrip cells={m.cells} step={step} w={w} h={h} /> : null}
    </div>
  );
};

/** ROOT: the window and its plates while open */
export const WindowView: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const o = T.win(frame);
  if (o <= 0) return null;
  const W = T.windowInfo;
  const w = W.box.x1 - W.box.x0;
  const h = W.box.y1 - W.box.y0;
  const step = T.strip(frame);
  return (
    <WindowFrame box={W.box} open={o} radius={W.radius} frame={W.frame}>
      {W.plates.map((m) => {
        const a = T.plate(m.id, frame);
        return a > 0 ? <Plate key={m.id} m={m} frame={frame} w={w} h={h} alpha={a} step={step} /> : null;
      })}
    </WindowFrame>
  );
};

/** ROOT (overlay plane): the ONE tag of the plate on screen, bottom-right inside the window, on EVERY frame the window is
 *  visible (lesson 31: it shares the window's first frame); a closing window below 30 % takes its tag with it (video 14 B11). */
export const WindowTags: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const o = T.win(frame);
  const tag = T.tagAt(frame);
  if (!tag || o <= 0) return null;
  const closing = o < 1 && T.win(frame + 1) < o;
  if (closing && o < 0.3) return null;
  const b = T.windowInfo.box;
  // a tag wider than the window (the Marey credit) sits just UNDER the window, left-aligned, instead of spilling over its frame
  const below = measure(tag, "mono", 24) + 24 > b.x1 - b.x0 - 28;
  const pos: React.CSSProperties = below ? { left: b.x0, top: b.y1 + 10 } : { right: 1080 - (b.x1 - 14), top: b.y1 - 52 };
  return (
    <div style={{ position: "absolute", ...pos, height: 38, padding: "0 12px", display: "flex", alignItems: "center",
      backgroundColor: rgba(C.shadow, 0.82), borderRadius: 6, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.bone, whiteSpace: "nowrap",
      opacity: Math.min(1, o), transform: `scale(${0.96 + 0.04 * Math.min(1, o)})`, transformOrigin: below ? "0% 0%" : "100% 100%" }}>
      {tag}
    </div>
  );
};
