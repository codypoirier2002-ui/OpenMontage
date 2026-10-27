// TEMPORARY stub label (foundation stage): every stub scene shows a labelled card in the TOP UI band (y 14-...) on the
// OVERLAY plane with its id, unit, frames and subject. Builders delete the <StubLabel> from their scenes; delete this file
// when the last stub is gone. Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, rgba } from "../theme";
import type { SceneId } from "../types";

export const INFO: Record<SceneId, { name: string; unit: string; subject: string }> = {
  sc01: { name: "CatDrop", unit: "U1", subject: "root: rig + clamp + header + checklist + 'drawn · not to scale' from f0; clamp OPENS on clampOpen (X1). U1: <CatLive/> (hangs, falls, preview flip, ghost)" },
  sc02: { name: "NothingToPush", unit: "U1", subject: "root: window opens ON windowOpen1 (S1, X2) + 'AI impression'. U1: readouts 'push: none' / 'starting spin: 0' tick to values on readouts[0..1] (right column x 640-920, y 620-780)" },
  sc03: { name: "Marey1894", unit: "U1", subject: "root: S1 -> Marey strip crossfade + HARD tag swap; strip steps. U1: 'IMPOSSIBLE?' <Stamp> SEATED ON stampImpossible (X3) in the Overlay" },
  sc04: { name: "FindUp", unit: "U1", subject: "root: '01 FIND UP' ticks ON tick01 (X4); clock starts. U1: <CatLive/> reset upside down; <InnerEarIcon> glows from innerEar; 'UP' arrow seats ON tick01; label 'inner ear: which way is up'" },
  sc05: { name: "Bend", unit: "U1", subject: "U1: <CatLive axes/> bends (bendStart X5 -> bendSeat), axes; <DialsLive/> in on dialsIn, 'total spin: 0' on totalSeat; '02 BEND' ON tick02 (root)" },
  sc06: { name: "TuckFront", unit: "U1", subject: "HERO. U1: front legs tuck (tuckStart -> tuckSeat); FRONT turns fast, BACK a little the other way (turnStart X5 -> turnEnd); labels 'legs in → spins fast' / 'legs out → turns slowly'; '03 TUCK FRONT' ON tick03 (root). FOUNDATION DEMO here" },
  sc07: { name: "Skater", unit: "U2", subject: "U2: <CatLive/> holds; <Skater> inset arms out -> in on armsIn + 'smaller → spins faster' + its own 'drawn · not to scale' SceneTag" },
  sc08: { name: "Swap", unit: "U2", subject: "U2: legs swap (swapStart X5), BACK follows (backTurnStart -> swapEnd), FRONT back a little; '04 SWAP' ON tick04 (root)" },
  sc09: { name: "Land", unit: "U2", subject: "root: floor line from floorIn; '05 SPREAD' ON tick05, '06 LAND' + clock stop ON tick06; S2 window ON windowOpen2 (X2). U2: legs out, arch, paws CONTACT the floor ON land (X6)" },
  sc10: { name: "NotAlways", unit: "U2", subject: "U2: dials gone by dialsOut (root curves); 'NOT ALWAYS' <Stamp> SEATED ON stampNotAlways (X3, Overlay, across the card); short-drop ghost from shortStart, FRONT dial partial, gone by shortGone; label 'short drop: no time to turn' (PROBABLY grammar)" },
  sc11: { name: "TheStudy", unit: "U2", subject: "U2: <Ledger> SEATED ON ledgerSeat (X7), bar fills barFrom -> barTo, '~90% survived'" },
  sc12: { name: "NotCounted", unit: "U2", subject: "NO SFX. U2: ghost column 'never reached a vet' from ghostColumn, 'not counted' on notCounted, bracket 'of cats brought in' on bracket; nothing changes after vetEndFrame; CTA 'Seen a cat do this?' (root)" },
};

export const StubLabel: React.FC<{ id: SceneId; from: number; to: number }> = ({ id, from, to }) => {
  const frame = useCurrentFrame();
  const i = INFO[id];
  if (frame < from || frame >= to) return null;
  const row: React.CSSProperties = { fontFamily: FONT.mono, fontWeight: 400, fontSize: 17, color: C.bone, lineHeight: 1.22 };
  return (
    <div style={{ position: "absolute", left: 40, top: 14, width: 1000, padding: "6px 16px", boxSizing: "border-box", backgroundColor: rgba(C.nightInk, 0.9), border: `2px dashed ${C.steel}`, borderRadius: 4 }}>
      <div style={{ fontFamily: FONT.mono, fontWeight: 500, fontSize: 17, letterSpacing: "0.04em", color: C.steel }}>
        STUB · {id} · {i.unit} · f {from}–{to} · {to - from} f · {((to - from) / 30).toFixed(2)} s
      </div>
      <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 26, color: C.bone, lineHeight: 1.15 }}>{i.name}</div>
      <div style={row}>{i.subject}</div>
    </div>
  );
};
