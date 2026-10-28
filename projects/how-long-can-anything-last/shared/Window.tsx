// THE WINDOW (ROOT ONLY: Composition.tsx mounts <WindowView/> once; props.window, build_props.py; its ONE tag is root too:
// <WindowTags/> on the overlay plane, keyed to the state that is actually showing). Video 18's window, re-used:
//   ONE portrait box x 580-920, y 440-893 (theme.ts L.win), rounded 22 px, a 6 px steel frame + a 1 px lit rim + an inner shadow
//   S1    sc03        a giant tortoise (AI impression), open ON windowOpen1
//   S2    sc04        a Greenland shark, crossfading in over XFADE_F from plateSwap1 (hard tag swap at the midpoint, lesson 38)
//   S3    sc05        a bristlecone pine, crossfading in from plateSwap2; the window closes from windowClose1
//   SUN   sc06-sc07   the DRAWN Sun + red dwarf (shared/Devices.tsx <SunDrawing/>, 'drawn · not to scale'), open ON windowOpen2
//   TANK  sc08-sc11   the DRAWN detector tank (<TankDrawing/>, 'drawn · not to scale'), open ON windowOpen3, closes from windowClose3
// Opens over 6 f (ease-out, first visible frame ON its key frame), closes over 8 f (first moving frame ON its key frame).
// Hooks at the top (lesson 1). No blend modes (lesson 24).

import React from "react";
import { Img, staticFile, useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { prog, useT } from "../time";
import type { WindowPlate } from "../types";
import { SunDrawing, TankDrawing } from "./Devices";

export const WindowFrame: React.FC<{ open: number; children?: React.ReactNode }> = ({ open, children }) => {
  const b = L.win;
  const w = b.x1 - b.x0;
  const h = b.y1 - b.y0;
  const k = Math.max(0, Math.min(1, open)); // the ease lives in props.window.open (no second ease on top)
  return (
    <div style={{ position: "absolute", left: b.x0, top: b.y0, width: w, height: h, opacity: k, transform: `scale(${0.96 + 0.04 * k})`, transformOrigin: "50% 50%" }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: b.r, overflow: "hidden", backgroundColor: C.chip, boxShadow: "0 18px 50px rgba(0,0,0,0.6)" }}>
        {children}
        <div style={{ position: "absolute", inset: 0, borderRadius: b.r, boxShadow: "inset 0 0 40px rgba(7,10,18,0.55)" }} />
      </div>
      <div style={{ position: "absolute", inset: -b.frame / 2, borderRadius: b.r + b.frame / 2, border: `${b.frame}px solid ${C.steelDim}` }} />
      <div style={{ position: "absolute", inset: b.frame / 2, borderRadius: b.r - b.frame / 2, border: `1px solid ${rgba(C.steel, 0.7)}` }} />
    </div>
  );
};

const Plate: React.FC<{ m: WindowPlate; frame: number }> = ({ m, frame }) => {
  const b = L.win;
  const push = m.push[0] + (m.push[1] - m.push[0]) * prog(frame, m.pushFrom, m.pushTo);
  if (m.base === null) {
    return (
      <div style={{ position: "absolute", inset: 0, transform: `scale(${push})`, transformOrigin: "50% 50%" }}>
        {m.id === "SUN" ? <SunDrawing w={b.x1 - b.x0} h={b.y1 - b.y0} /> : <TankDrawing w={b.x1 - b.x0} h={b.y1 - b.y0} />}
      </div>
    );
  }
  return (
    <Img src={staticFile(m.base)} style={{ position: "absolute", left: 0, top: 0, width: b.x1 - b.x0, height: b.y1 - b.y0, transform: `scale(${push})`, transformOrigin: "50% 50%" }} />
  );
};

/** ROOT: the window and its plates while it is open */
export const WindowView: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const open = T.win(frame);
  if (open <= 0) return null;
  const live = T.windowInfo.plates.map((m) => ({ m, a: T.plate(m.id, frame) })).filter((x) => x.a > 0);
  return (
    <WindowFrame open={open}>
      {live.map(({ m, a }) => (
        <div key={m.id} style={{ position: "absolute", inset: 0, opacity: a }}>
          <Plate m={m} frame={frame} />
        </div>
      ))}
    </WindowFrame>
  );
};

/** ROOT (overlay plane): the window's ONE tag ('AI impression' / 'drawn · not to scale'), tied to the plate that is actually showing (hard swap at a
 *  crossfade's midpoint, lesson 38); fades with the window */
export const WindowTags: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const open = T.win(frame);
  const tag = T.tagAt(frame);
  if (open <= 0 || !tag) return null;
  const b = L.win;
  return (
    <div style={{ position: "absolute", right: L.W - (b.x1 - 16), top: b.y1 - 54, height: 38, padding: "0 12px", display: "flex", alignItems: "center",
      backgroundColor: rgba(C.shadow, 0.82), borderRadius: 6, fontFamily: FONT.mono, fontWeight: 400, fontSize: 24, color: C.bone, whiteSpace: "nowrap",
      opacity: Math.max(0, Math.min(1, open)) }}>
      {tag}
    </div>
  );
};
