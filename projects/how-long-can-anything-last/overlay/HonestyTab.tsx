// KIT TEMPLATE (docs/channel/kit, taken from video 14, QA passed). Copied by new_project.sh; the comments below describe
// video 14 - rewrite them for this video. Contract with theme.ts / time.ts / types.ts: docs/channel/kit/KIT.md.
// The honesty meter (channel standard; copied from projects/how-hot-can-it-get/overlay/HonestyTab.tsx, video 13 (itself videos 10-12), QA
// passed, incl. its fixes: the sublabel keys on the caption page's FIRST frame; IDLE = no capsule, even words): a smoked-glass tab on the caption
// slab's top edge, x 140-628, y 1236-1290. MEASURED · PROBABLY · MAYBE in Spline Sans Mono 600 24 px caps; inactive
// words Bone 38 %.
//   MEASURED  solid Bone capsule, Night Ink text
//   PROBABLY  2 px Bone outline + 45° hatch          (the vibration, the one-study miss rate, peeing while feeding)
//   MAYBE     dashed ghost (UNUSED in this film)
//   IDLE      tab at 70 %, NO capsule, the three words even (QA B5, fix round 1: a grey pill on MEASURED read as a dim
//             MEASURED claim on a line with no claim). Frame 0, the closing line 'By then, she's long gone.', the settle. The capsule fades
//             in / out with the glide out of / into IDLE (a continuous idle weight: no pop at mid-glide)
// + SUBLABEL (none in this film's plan; supported: Spline Sans Mono 600 18 px on a glass chip right of the tab).
// Schedule (props.meter, build_props.py CLAIMS -> script.json claim_tags): each key sits on the START
// of the caption page that carries the claim (lesson 3; no two claims on one page, asserted); a state shows ONLY while its
// claim is on screen. Glide: 12 f on bezier(0.7,0,0.3,1) from `glideStart` (6 f before the page). A key that repeats the
// previous state (a new section's claim, or a new sublabel) does not glide: the capsule pulses (a 10 f Bone glow).

import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, E, FONT, L, glass } from "../theme";
import { flicker } from "../shared/noise";
import { prog } from "../time";
import type { MeterKey, MeterState } from "../types";

const ADV = 24 * 0.6 + 1.5; // Spline Sans Mono advance (0.6 em) + 1.5 px tracking
const WORDS = [
  { key: "MEASURED", x: 22 },
  { key: "PROBABLY", x: 204 },
  { key: "MAYBE", x: 386 },
] as const;
const PAD = 12;
const slotOf = (k: string) => {
  const w = WORDS.find((x) => x.key === k)!;
  return { x: w.x - PAD, w: w.key.length * ADV + PAD * 2 };
};
const SLOT: Record<MeterState, { x: number; w: number }> = {
  IDLE: slotOf("MEASURED"),
  MEASURED: slotOf("MEASURED"),
  PROBABLY: slotOf("PROBABLY"),
  MAYBE: slotOf("MAYBE"),
};
/** IDLE: every word at the same alpha (no emphasis on MEASURED) */
const IDLE_WORD = 0.6;
const ACTIVE_WORD: Record<MeterState, string> = { IDLE: "MEASURED", MEASURED: "MEASURED", PROBABLY: "PROBABLY", MAYBE: "MAYBE" };

const word = (left: number): React.CSSProperties => ({
  position: "absolute",
  left,
  top: 0,
  height: L.tab.h,
  display: "flex",
  alignItems: "center",
  fontFamily: FONT.tab,
  fontWeight: 600,
  fontSize: 24,
  letterSpacing: 1.5,
  whiteSpace: "nowrap",
});

export const HonestyTab: React.FC<{ keys: MeterKey[] }> = ({ keys }) => {
  const frame = useCurrentFrame();
  // the current key = the last whose glide has started; `from` = the last key with a DIFFERENT state before it
  let i = 0;
  for (let k = 0; k < keys.length; k++) if (frame >= keys[k].glideStart) i = k;
  let j = i;
  while (j > 0 && keys[j].repeat) j--;
  const cur = keys[j];
  const prev = keys[Math.max(0, j - 1)];
  const g = j === 0 ? 1 : interpolate(frame, [cur.glideStart, cur.glideStart + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: E.meter });
  // into / out of IDLE the capsule does not slide (it only fades where its claim was / will be)
  const a = SLOT[prev.state === "IDLE" ? cur.state : prev.state];
  const b = SLOT[cur.state === "IDLE" ? prev.state : cur.state];
  const x = a.x + (b.x - a.x) * g;
  const w = a.w + (b.w - a.w) * g;
  const state: MeterState = g < 0.5 ? prev.state : cur.state; // fill style morphs at mid-glide
  const rep = keys[i].repeat ? keys[i] : null;
  const pulse = rep ? (frame < rep.frame ? prog(frame, rep.glideStart, rep.frame) : 1 - prog(frame, rep.frame, rep.frame + 10)) : 0;
  // the idle weight: 1 = fully idle (no capsule, even words, tab 70 %), continuous through a glide into / out of IDLE
  const idleW = prev.state === "IDLE" && cur.state === "IDLE" ? 1 : prev.state === "IDLE" ? 1 - g : cur.state === "IDLE" ? g : 0;
  // the claim state the capsule shows while it fades (the non-idle side of the glide)
  const vis: MeterState = state !== "IDLE" ? state : prev.state !== "IDLE" ? prev.state : cur.state;
  const ghost = vis === "MAYBE" ? flicker("meter", frame) : 1;
  const capH = 38;
  const capTop = (L.tab.h - capH) / 2;

  const capsule: React.CSSProperties =
    vis === "IDLE"
      ? { opacity: 0 }
      : vis === "MEASURED"
        ? { backgroundColor: C.bone, boxShadow: pulse > 0 ? `0 0 ${16 * pulse}px rgba(244,239,230,${0.8 * pulse})` : undefined }
        : vis === "PROBABLY"
          ? {
              border: `2px solid ${C.bone}`,
              backgroundImage: "repeating-linear-gradient(45deg, rgba(244,239,230,0.3) 0 2px, transparent 2px 7px)",
              boxShadow: pulse > 0 ? `0 0 ${16 * pulse}px rgba(244,239,230,${0.6 * pulse})` : undefined,
            }
          : { border: `2px dashed ${C.bone}`, backgroundColor: "rgba(244,239,230,0.10)", opacity: ghost };
  const capA = (capsule.opacity === undefined ? 1 : Number(capsule.opacity)) * (1 - idleW);

  const solid = vis === "MEASURED";
  // QA A-1 (fix round 1): the SUBLABEL keys on the key's own `frame` (the caption page's first frame), not on its
  // glideStart: the outgoing chip holds to the frame before, the incoming one shows from its frame (3 f fade-in starting
  // there), so the chip changes together with the state word.
  let iSub = 0;
  for (let k = 0; k < keys.length; k++) if (frame >= keys[k].frame) iSub = k;
  const sub = keys[iSub].sublabel;
  const subA = sub ? Math.min(1, (frame - keys[iSub].frame + 1) / 3) : 0;
  // the chip must end <= x 912: '"probably" - 1888 report' / 'conversion · lower bound' (24 chars) set at ~16.8 px
  const subSize = Math.min(18, (L.sublabel.w - 28) / (Math.max(1, sub.length) * (0.6 + 0.5 / 18)));
  return (
    <>
    {sub && subA > 0 ? (
      <div style={{ position: "absolute", left: L.sublabel.x, top: L.sublabel.y, height: L.sublabel.h, padding: "0 14px", display: "flex", alignItems: "center",
        borderRadius: 12, ...glass(0.62), fontFamily: FONT.tab, fontWeight: 600, fontSize: subSize, letterSpacing: 0.5, color: C.bone, opacity: 0.88 * subA, whiteSpace: "nowrap" }}>
        {sub}
      </div>
    ) : null}
    <div
      style={{
        position: "absolute",
        left: L.tab.x,
        top: L.tab.y,
        width: L.tab.w,
        height: L.tab.h,
        borderRadius: "16px 16px 6px 6px",
        opacity: 1 - 0.3 * idleW,
        ...glass(0.62),
      }}
    >
      {capA > 0 ? <div style={{ position: "absolute", left: x, top: capTop, width: w, height: capH, borderRadius: capH / 2, boxSizing: "border-box", ...capsule, opacity: capA }} /> : null}
      {WORDS.map((wd, k) => {
        const on = ACTIVE_WORD[vis] === wd.key;
        const color = C.bone;
        const claimAlpha = on ? (vis === "MAYBE" ? ghost : 1) : 0.38;
        const alpha = claimAlpha + (IDLE_WORD - claimAlpha) * idleW;
        return (
          <React.Fragment key={wd.key}>
            {k > 0 ? <span style={{ ...word(wd.x - 30), color: C.bone, opacity: 0.38 }}>·</span> : null}
            <span style={{ ...word(wd.x), color, opacity: alpha }}>{wd.key}</span>
          </React.Fragment>
        );
      })}
      {solid && capA > 0 ? (
        // Night Ink copy of the words, clipped to the solid capsule (letters it slides off stay Bone)
        <div style={{ position: "absolute", left: x, top: capTop, width: w, height: capH, overflow: "hidden", opacity: capA }}>
          {WORDS.map((wd) => (
            <span key={wd.key} style={{ ...word(wd.x - x), top: -capTop, color: C.nightInk }}>
              {wd.key}
            </span>
          ))}
        </div>
      ) : null}
    </div>
    </>
  );
};
